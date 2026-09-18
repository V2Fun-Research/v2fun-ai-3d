#!/usr/bin/env python3
"""Read-only GLB metadata inventory. Python 3 stdlib; no renderer or geometry decoder.

Counts triangles for TRIANGLES/STRIP/FAN, including default-scene node instances.
Reports primitive-local accessor bounds, never labels them world-space measurements.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def index(items, value, label):
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < len(items):
        raise ValueError('Invalid ' + label + ' index: ' + repr(value))
    return items[value]


def inspect(path):
    size = path.stat().st_size
    with path.open('rb') as f:
        header = f.read(12)
        if len(header) != 12:
            raise ValueError('Truncated GLB header')
        magic, version, declared = struct.unpack('<4sII', header)
        if magic != b'glTF' or version != 2 or declared != size:
            raise ValueError('Invalid GLB magic, version, or declared byte length')
        raw = f.read(8)
        if len(raw) != 8:
            raise ValueError('Missing JSON chunk')
        length, kind = struct.unpack('<II', raw)
        if kind != 0x4E4F534A or length % 4 or length > size - 20:
            raise ValueError('Invalid first JSON chunk')
        doc = json.loads(f.read(length).decode('utf-8').rstrip(' \x00'))
        while f.tell() < size:
            chunk = f.read(8)
            if len(chunk) != 8:
                raise ValueError('Truncated chunk header')
            length, kind = struct.unpack('<II', chunk)
            if length % 4 or length > size - f.tell():
                raise ValueError('Truncated or unaligned chunk')
            f.seek(length, 1)
    if not isinstance(doc, dict) or doc.get('asset', {}).get('version') != '2.0':
        raise ValueError('JSON asset is not glTF 2.0')
    accessors = doc.get('accessors', [])
    records, counts, warnings = [], [], []
    for mi, mesh in enumerate(doc.get('meshes', [])):
        total = 0
        for pi, primitive in enumerate(mesh.get('primitives', [])):
            position = index(accessors, primitive.get('attributes', {}).get('POSITION'), 'POSITION accessor')
            count_accessor = index(accessors, primitive['indices'], 'index accessor') if 'indices' in primitive else position
            count = count_accessor.get('count')
            if not isinstance(count, int) or count < 0:
                raise ValueError('Invalid accessor count')
            mode = primitive.get('mode', 4)
            if mode not in range(7):
                raise ValueError('Invalid primitive mode')
            triangles = count // 3 if mode == 4 else max(0, count - 2) if mode in (5, 6) else 0
            if mode == 4 and count % 3:
                warnings.append('Mesh %d primitive %d TRIANGLES count not divisible by 3' % (mi, pi))
            total += triangles
            records.append({'mesh': mi, 'primitive': pi, 'name': mesh.get('name'),
                            'vertices': position.get('count'), 'triangles': triangles,
                            'mode': mode, 'localAccessorBounds': [position.get('min'), position.get('max')],
                            'material': primitive.get('material'), 'attributes': sorted(primitive.get('attributes', {}))})
        counts.append(total)
    nodes, scenes = doc.get('nodes', []), doc.get('scenes', [])
    if scenes:
        roots = index(scenes, doc.get('scene', 0), 'scene').get('nodes', [])
    else:
        children = {n for node in nodes for n in node.get('children', [])}
        roots = [i for i in range(len(nodes)) if i not in children]
        warnings.append('No scenes declared; count inferred from parentless nodes')
    gpu_instanced = any('EXT_mesh_gpu_instancing' in n.get('extensions', {}) for n in nodes)
    def visit(ni, ancestors):
        if ni in ancestors:
            raise ValueError('Cyclic node hierarchy')
        node = index(nodes, ni, 'node')
        own = index(counts, node['mesh'], 'mesh') if 'mesh' in node else 0
        return own + sum(visit(c, ancestors | {ni}) for c in node.get('children', []))
    scene_triangles = sum(visit(n, set()) for n in roots)
    if gpu_instanced:
        scene_triangles = None
        warnings.append('EXT_mesh_gpu_instancing present: scene count requires instance attribute decoding')
    if doc.get('extensionsRequired'):
        warnings.append('Required extensions must be supported by the rendering importer')
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    return {'path': str(path.resolve()), 'bytes': size, 'sha256': digest.hexdigest(),
            'format': 'GLB 2.0', 'uniqueMeshTriangles': sum(counts),
            'defaultSceneTriangles': scene_triangles, 'primitives': records,
            'nodeCount': len(nodes), 'nodes': nodes, 'materialCount': len(doc.get('materials', [])),
            'images': doc.get('images', []),
            'externalResources': [r['uri'] for r in doc.get('images', []) + doc.get('buffers', [])
                                  if 'uri' in r and not r['uri'].startswith('data:')],
            'extensionsRequired': doc.get('extensionsRequired', []), 'warnings': warnings,
            'scope': 'Metadata only; not render, UV quality, geometry integrity, orientation or world bounds validation'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--recursive', action='store_true', help='Also scan subdirectories')
    args = parser.parse_args()
    if not args.input.exists():
        parser.error('Input does not exist')
    files = [args.input] if args.input.is_file() else sorted(args.input.rglob('*') if args.recursive else args.input.iterdir())
    if args.out:
        if args.input.is_file() and args.out.resolve() == args.input.resolve():
            parser.error('--out must not overwrite an input file')
        if args.out.exists():
            with args.out.open('rb') as f:
                if f.read(4) == b'glTF':
                    parser.error('--out must not overwrite a GLB asset')
        files = [p for p in files if p.resolve() != args.out.resolve()]
    result = {'assets': [], 'errors': [], 'skippedNonGLB': 0}
    for path in files:
        if not path.is_file():
            continue
        try:
            with path.open('rb') as f:
                is_glb = f.read(4) == b'glTF'
            if not is_glb and path.suffix.lower() != '.glb':
                result['skippedNonGLB'] += 1
                if args.input.is_file():
                    raise ValueError('Not GLB; inspect using the appropriate format importer')
                continue
            result['assets'].append(inspect(path))
        except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as exc:
            result['errors'].append({'path': str(path), 'error': str(exc)})
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + '\n', encoding='utf-8')
        print('GLB assets: %d; errors: %d; report: %s' % (len(result['assets']), len(result['errors']), args.out))
    else:
        print(text)
    return 1 if result['errors'] or not result['assets'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
