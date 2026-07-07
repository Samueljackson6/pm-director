"""添加 pnpm overrides 到 ui-vben/package.json 并验证"""
import json, sys
path = sys.argv[1]
d = json.load(open(path))
d.setdefault('pnpm', {})
d['pnpm'].setdefault('overrides', {})
d['pnpm']['overrides']['jiti'] = '2.6.1'
json.dump(d, open(path, 'w'), indent=2)
print('Added jiti override:', d['pnpm']['overrides'])
