import time, sys
from playwright.sync_api import sync_playwright
S = sys.argv[1]; U = 'http://127.0.0.1:5058'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900})
    pg.goto(U + '/'); pg.set_input_files('#vcf', '/home/claude/appdev/pharmageno_test_v8m/exemples/NA19085.vcf'); pg.select_option('#specialite', label='Cardiologie'); pg.click('button[type=submit]')
    t0 = time.time(); best = 0
    while time.time() - t0 < 420:
        time.sleep(4)
        txt = pg.inner_text('body')
        if 'Résultat' in txt.split('\n')[2:4].__str__() or '/resultats/' in pg.url: break
        try: w = pg.eval_on_selector('.bar, .barre, [role=progressbar], #barre, #bar', 'e => e.textContent')
        except Exception: w = ''
        print(round(time.time()-t0), pg.url.split('/')[-2:], repr(txt[:140].replace('\n',' | ')), w, flush=True)
        if 15 < time.time() - t0 and best == 0 and '/progression/' in pg.url: pg.screenshot(path=S + '/3b_progression_en_cours.png'); best = 1
        if best == 1 and time.time() - t0 > 60: pg.screenshot(path=S + '/3c_progression_suite.png'); best = 2
    print('FIN', pg.url, round(time.time()-t0)); time.sleep(2)
    jid = pg.url.rstrip('/').split('/')[-1].split('?')[0]; open(S + '/jid.txt', 'w').write(jid)
    for d in pg.query_selector_all('details'):
        try: d.evaluate('e => e.open = true')
        except Exception: pass
    pg.screenshot(path=S + '/6_resultats_complet_ouvert.png', full_page=True)
    pg.goto(U + '/patient/' + jid); pg.screenshot(path=S + '/7_vue_patient.png', full_page=True)
    pg.goto(U + '/apropos'); pg.screenshot(path=S + '/8_methode_limites.png', full_page=True)
    b.close()
