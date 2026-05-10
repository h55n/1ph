#!/bin/bash
# Test a single connector without running the full pipeline
# Usage: ./scripts/test_pipeline.sh mlh
# Usage: ./scripts/test_pipeline.sh dorahacks

CONNECTOR=${1:-mlh}
echo "🧪 Testing connector: $CONNECTOR"
echo ""

cd "$(dirname "$0")/.."

python3 - <<EOF
import sys
sys.path.insert(0, '.')

connector_map = {
    'mlh':          'pipeline.connectors.mlh.MLHConnector',
    'dorahacks':    'pipeline.connectors.dorahacks.DoraHacksConnector',
    'hackerearth':  'pipeline.connectors.hackerearth.HackerEarthConnector',
    'devfolio':     'pipeline.connectors.devfolio.DevfolioConnector',
    'hack2skill':   'pipeline.connectors.hack2skill.Hack2SkillConnector',
    'startup_india':'pipeline.connectors.startup_india.StartupIndiaConnector',
    'devpost':      'pipeline.connectors.devpost.DevpostConnector',
    'unstop':       'pipeline.connectors.unstop.UnstopConnector',
}

name = '${CONNECTOR}'.lower()
if name not in connector_map:
    print(f'Unknown connector: {name}')
    print(f'Available: {", ".join(connector_map.keys())}')
    sys.exit(1)

module_path, class_name = connector_map[name].rsplit('.', 1)
import importlib
module = importlib.import_module(module_path)
ConnectorClass = getattr(module, class_name)

connector = ConnectorClass()
result = connector.run()

print(f'Source:  {result.source}')
print(f'Status:  {result.status}')
print(f'Records: {len(result.records)}')
if result.error:
    print(f'Error:   {result.error}')
print()

for i, r in enumerate(result.records[:5]):
    print(f'[{i+1}] {r.title[:60]}')
    print(f'     URL: {r.apply_url[:70]}')
    print(f'     Org: {r.organizer_name}')
    print(f'     Close: {r.registration_close}')
    print()

if len(result.records) > 5:
    print(f'... and {len(result.records) - 5} more')
EOF
