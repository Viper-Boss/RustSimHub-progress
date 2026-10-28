# SPDX-License-Identifier: AGPL-3.0-only
"""Rebuild only the public viewer; this does not validate or accept product work."""
from pathlib import Path
import argparse,json

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check',action='store_true')
args=parser.parse_args()
data=json.loads((root/'progress.json').read_text(encoding='utf8'))
assert data['schema']==1
milestones=data['original_milestones']
assert sum(m['weight'] for m in milestones)==100
assert all(0<=m['done_points']<=m['weight'] for m in milestones)
original=sum(m['done_points'] for m in milestones)
template=(root/'src/index.template.html').read_text(encoding='utf8')
template=template.replace('{{MILESTONE_PERCENT}}',f'{original:g}').replace('{{MILESTONE_REMAINING}}',f'{100-original:g}')
payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
css=(root/'src/dashboard.css').read_text(encoding='utf8')+'\n'+(root/'src/team.css').read_text(encoding='utf8')
script=(root/'src/dashboard.mjs').read_text(encoding='utf8')
assert '</script' not in script.lower() and '</style' not in css.lower()
rendered=template.replace('<!-- DASHBOARD_STYLE -->','<style>\n'+css+'\n</style>').replace('<!-- DASHBOARD_DATA -->','<script id="progress-data" type="application/json">'+payload+'</script>').replace('<!-- DASHBOARD_SCRIPT -->','<script type="module">\n'+script+'\n</script>')
output=root/'index.html'
if args.check:
    assert output.read_bytes()==rendered.encode('utf8'),'generated viewer is stale'
else:
    output.write_bytes(rendered.encode('utf8'))
print('Public viewer matches snapshot; no product acceptance was changed.')
