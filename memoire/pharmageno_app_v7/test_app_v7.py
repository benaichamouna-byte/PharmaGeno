import sys, types, re, os, shutil
sys.argv=['x']
import app_pharmageno_v7 as A
cfg=types.SimpleNamespace(modeles='modeles',domaine='domaine_v7.json',atc='atc_mapping_medicaments_v1.csv',specialites='specialite_atc_v1.csv',
  alternatives='alternatives_atc4_v1.csv',codage='codage_pypgx_valeur_v7.csv',bundle=os.path.expanduser('~/pypgx-bundle'),travail='tw',taille_max_mo=50)
shutil.rmtree('tw',ignore_errors=True)
app=A.creer_app(cfg); c=app.test_client()
r=c.get('/'); print('index',r.status_code, 'Endocrinologie' in r.get_data(as_text=True))
for sp in ['Cardiologie','Psychiatrie','Hématologie','Oncologie']:
    r=c.post('/demo',data={'specialite':sp}); assert r.status_code==302,r.status_code
    loc=r.headers['Location']; jid=loc.rsplit('/',1)[1]
    r=c.get(loc); t=r.get_data(as_text=True); print(sp,r.status_code,len(t),'Traceback' in t)
    r=c.get(loc+'?q=warfarine'); t=r.get_data(as_text=True); print('  q warfarine',r.status_code,'Adaptation de dose' in t)
    r=c.get(loc+'?q=doliprane'); print('  q doliprane',r.status_code,'non trouvé' in r.get_data(as_text=True))
    r=c.get('/pdf/'+jid+'?q=clopidogrel'); print('  pdf',r.status_code,r.mimetype,len(r.data)); open('demo_%s.pdf'%sp[:4],'wb').write(r.data)
r=c.post('/demo',data={'specialite':'Urologie'}); print('urologie ->',r.headers['Location'])
r=c.post('/analyser',data={'specialite':'Cardiologie'}); print('sans fichier ->',r.headers['Location'])
import io
r=c.post('/analyser',data={'specialite':'Cardiologie','vcf':(io.BytesIO(b'ceci n est pas un vcf'),'x.vcf')},content_type='multipart/form-data'); loc=r.headers['Location']; print('faux vcf ->',loc)
import time
for _ in range(20):
    j=c.get('/etat/'+loc.rsplit('/',1)[1]).get_json()
    if j['etat']!='en_cours': break
    time.sleep(0.5)
print(j)
r=c.get(loc); print(r.status_code,'Fichier refusé' in r.get_data(as_text=True))
r=c.post('/supprimer/'+jid); print('suppr',r.status_code, os.path.exists('tw/jobs/%s.json'%jid))
print(c.get('/resultats/zzzzzzzzzzzz').status_code, c.get('/resultats/../../etc').status_code)
