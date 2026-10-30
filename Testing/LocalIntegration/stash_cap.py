import json,ssl,urllib.request,zlib,uuid
from pathlib import Path
def entry(i):return (1624453*(0x65F6D+i)+1023920427)%0x8ED7A18D
def pack(data):
 b=bytearray(len(data).to_bytes(4,'little')+data);start=len(b)%0xAAB
 for i in range(len(b)-1,0,-1):j=entry(i+start)%i;b[i],b[j]=b[j],b[i]
 return b
def unpack(data):
 b=bytearray(data);start=len(b)%0xAAB
 for i in range(1,len(b)):j=entry(i+start)%i;b[i],b[j]=b[j],b[i]
 n=int.from_bytes(b[:4],'little');assert n<=len(b)-4
 return b[4:4+n]

import argparse, concurrent.futures, shutil
parser=argparse.ArgumentParser(description="Stateful stash-cap regression: purchases 80 rows on a disposable LocalBuildTest account; requires local FreeTarcoins test-credit endpoint.")
parser.add_argument('--runtime',required=True)
parser.add_argument('--profile',required=True)
parser.add_argument('--output',required=True)
parser.add_argument('--bundle-ownership',action='store_true')
args=parser.parse_args()
root=Path(args.runtime)/'user/profiles'
session=args.profile
if len(session)!=24 or any(c not in '0123456789abcdef' for c in session):
 raise ValueError('Expected a 24-hex profile ID')
fixture=root/(session+'.json')
output=Path(args.output)
output.mkdir(parents=True,exist_ok=False)
shutil.copy2(fixture,output/'profile-before.json')
def profile(): return json.loads(fixture.read_text(encoding='utf-8-sig'))
assert profile()['info']['username'].startswith('LocalBuildTest')
assert not profile().get('purchasedShopStashRows')
others = {p: p.read_bytes() for p in root.glob('*.json') if p != fixture}
def send(path, body):
    shop = path.startswith('/v2/shop')
    payload = json.dumps(body).encode()
    req = urllib.request.Request('https://127.0.0.1:6969' + path, data=payload if shop else pack(zlib.compress(payload)),
        headers={'Content-Type':'application/json','Cookie':'PHPSESSID=' + session})
    with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=30) as response: data=response.read()
    if not shop: data=unpack(data)
    try: data=zlib.decompress(data)
    except zlib.error: pass
    return json.loads(data)
def buy(offer, count=1): return send('/v2/shop/api/v1/purchase/single', {'offerId':offer,'count':count})['data']['success']
def rejected(offer, count=1):
    before=profile()
    assert not buy(offer,count)
    after=profile()
    for key in ['purchasedShopStashRows','purchasedShopOffers']:
        assert after.get(key)==before.get(key),key
    for key in ['TarCoinBalance','Bonuses','Inventory']:
        assert after['characters']['pmc'].get(key)==before['characters']['pmc'].get(key),key
two='6a46981da1132c0a632db21c'
twenty='69c511e281e467e8b07f2d4a'
eighty='6a2a879b62d8a4e121a50a86'
assert send('/freetarcoins/add', {'amount':100000,'requestId':str(uuid.uuid4())})['Success']
import sys
if args.bundle_ownership:
    assert buy(twenty)
    rejected(twenty)
    assert buy('69c512738bd3e988e7ee0089')
    assert profile()['purchasedShopStashRows']==80
    assert all(p.read_bytes()==data for p,data in others.items())
    print('PASS: 20+60=80 allowed; same 20 bundle repeat rejected without charge; personal profiles unchanged')
    sys.exit(0)
assert buy(two)
rejected(eighty)
rejected(two, 2147483647)
assert buy(twenty)
assert profile()['purchasedShopStashRows']==22
rejected('69c512738bd3e988e7ee0089')
with urllib.request.urlopen(f'https://127.0.0.1:6969/shop/{session}/catalog-item/{eighty}', context=ssl._create_unverified_context()) as response:
    html=response.read().decode()
assert 'This purchase would exceed the 80 extra stash-row limit.' in html
(output/'blocked-page.html').write_text(html,encoding='utf-8')
assert buy(two,28)
assert profile()['purchasedShopStashRows']==78
before=profile()['characters']['pmc']['TarCoinBalance']
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results=list(pool.map(lambda _:buy(two),range(2)))
assert sorted(results)==[False,True],results
after=profile()
assert after['purchasedShopStashRows']==80
assert sum(b['value'] for b in after['characters']['pmc']['Bonuses'] if b['type']=='StashRows')==80
assert after['characters']['pmc']['TarCoinBalance']==before-300
rejected(two)
assert all(p.read_bytes()==data for p,data in others.items())
print('PASS: 2+80 rejected; 2+20=22; 22+60 rejected; huge quantity rejected; 78+2=80; concurrent second purchase rejected; no charge or rows on rejection; blocked shop explanation rendered; personal profiles unchanged')
