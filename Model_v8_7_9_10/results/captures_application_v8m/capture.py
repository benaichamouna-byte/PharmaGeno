import re, time, sys
from playwright.sync_api import sync_playwright
S = sys.argv[1]; U = 'http://127.0.0.1:5058'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900})
    pg.goto(U + '/'); pg.screenshot(path=S + '/1_accueil.png', full_page=True)
    opts = pg.eval_on_selector_all('#specialite option', 'els => els.map(e => e.value + "|" + e.textContent)'); print(opts[:12])
    pg.set_input_files('#vcf', '/home/claude/appdev/pharmageno_test_v8m/exemples/NA19085.vcf')
    pg.select_option('#specialite', label='Cardiologie')
    pg.screenshot(path=S + '/2_formulaire_rempli.png', full_page=True)
    pg.click('button[type=submit]')
    time.sleep(6); pg.screenshot(path=S + '/3_progression.png'); print(pg.url)
    t0 = time.time()
    while '/resultats/' not in pg.url and time.time() - t0 < 300: time.sleep(3)
    print(pg.url, round(time.time() - t0))
    time.sleep(2); pg.screenshot(path=S + '/4_resultats_haut.png'); pg.screenshot(path=S + '/5_resultats_complet.png', full_page=True)
    open(S + '/url.txt', 'w').write(pg.url)
    b.close()
