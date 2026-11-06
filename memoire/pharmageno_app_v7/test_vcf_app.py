import sys, types, os, shutil, time, io
sys.argv=['x']
import app_pharmageno_v7 as A
S='/tmp/claude-0/-home-claude/8409b04b-17f7-52aa-bb79-1c3b814505b7/scratchpad'
def go(pgx, label):
    cfg=types.SimpleNamespace(modeles='modeles',domaine='domaine_v7.json',atc='atc_mapping_medicaments_v1.csv',specialites='specialite_atc_v1.csv',alternatives='alternatives_atc4_v1.csv',
      codage='codage_pypgx_valeur_v7.csv',bundle=S+'/pypgx-bundle',travail='tw3',taille_max_mo=50,pgx_python=pgx)
    app=A.creer_app(cfg); c=app.test_client()
    r=c.post('/analyser',data={'specialite':'Cardiologie','vcf':(open(S+'/pc/t.vcf','rb'),'pharmcat.example.vcf')},content_type='multipart/form-data')
    jid=r.headers['Location'].rsplit('/',1)[1]; t0=time.time(); last=None
    while time.time()-t0<260:
        j=c.get('/etat/'+jid).get_json()
        if j['message']!=last: print('  [%3ds] %3d%% %s'%(time.time()-t0,j['pct'],j['message'])); last=j['message']
        if j['etat']!='en_cours': break
        time.sleep(2)
    print(label,'->',j['etat'],'|',j['message'][:300] if j['etat']!='termine' else '')
    if j['etat']=='termine':
        h=c.get('/resultats/'+jid).get_data(as_text=True); open('res_vcf.html','w',encoding='utf-8').write(h)
        import re; print(re.sub(r'\s+',' ',re.search(r'Résumé</h2><p>(.*?)</p>',h,re.S).group(1)))
        print('PDF',c.get('/pdf/'+jid).status_code)
go(sys.executable,'A) mauvais environnement (sans PyPGx)')
go(S+'/instt/pgxenv/bin/python','B) environnement dédié')
