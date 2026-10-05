import json, random
random.seed(7)
els=[]
COL={'blue':'#a5d8ff','green':'#b2f2bb','yellow':'#ffec99','red':'#ffc9c9','violet':'#d0bfff','orange':'#ffd8a8',
     'grey':'#e9ecef','white':'#ffffff','dark':'#343a40','cyan':'#99e9f2','none':'transparent'}
FRAME=None
def base(t,x,y,w,h,**k):
    e=dict(id=f"{t}-{len(els)}-{random.randrange(10**8)}",type=t,x=x,y=y,width=w,height=h,angle=0,strokeColor="#1e1e1e",
        backgroundColor="transparent",fillStyle="solid",strokeWidth=2,strokeStyle="solid",roughness=1,opacity=100,groupIds=[],
        frameId=FRAME,roundness=None,seed=random.randrange(1,2**31),version=1,versionNonce=random.randrange(1,2**31),isDeleted=False,
        boundElements=None,updated=1,link=None,locked=False)
    e.update(k); return e
def text(x,y,s,size=20,align="center",w=None,color="#1e1e1e"):
    lines=s.split("\n"); w=w or max(len(l) for l in lines)*size*0.55; h=len(lines)*size*1.25
    if align=="center": x=x-w/2
    els.append(base("text",x,y,w,h,text=s,originalText=s,fontSize=size,fontFamily=1,textAlign=align,verticalAlign="top",
        containerId=None,lineHeight=1.25,strokeColor=color,autoResize=True))
def box(x,y,w,h,label="",color='blue',size=20,dashed=False,opacity=100,stroke="#1e1e1e",lcolor="#1e1e1e"):
    els.append(base("rectangle",x,y,w,h,backgroundColor=COL[color],roundness={"type":3},
        strokeStyle="dashed" if dashed else "solid",opacity=opacity,strokeColor=stroke))
    if label:
        n=label.count("\n")+1
        text(x+w/2,y+h/2-n*size*0.62,label,size,color=lcolor)
def group(x,y,w,h,label,color='none'):
    els.append(base("rectangle",x,y,w,h,backgroundColor=COL[color],roundness={"type":3},strokeStyle="dashed",strokeWidth=2))
    text(x+12,y+8,label,20,"left",w=w-24)
def arrow(x1,y1,x2,y2,color="#1e1e1e",dashed=False,label=None,both=False):
    els.append(base("arrow",x1,y1,x2-x1,y2-y1,points=[[0,0],[x2-x1,y2-y1]],lastCommittedPoint=None,startBinding=None,
        endBinding=None,startArrowhead="arrow" if both else None,endArrowhead="arrow",roundness={"type":2},strokeColor=color,
        strokeStyle="dashed" if dashed else "solid"))
    if label: text((x1+x2)/2,(y1+y2)/2-26,label,16,color="#5c5f66")
def note(x,y,s,w=440,color="#1e1e1e",size=18): text(x,y,s,size,"left",w=w,color=color)
def frame(x,y,w,h,name):
    global FRAME
    f=base("frame",x,y,w,h,name=name,frameId=None,strokeColor="#bbb",roughness=0)
    els.append(f); FRAME=f["id"]
    return x,y
def title(x,y,s,sub=None):
    text(x+30,y+25,s,30,"left",w=1100)
    if sub: text(x+30,y+68,sub,18,"left",w=1100,color="#5c5f66")
def doc(x,y,s,w=230):  # « manuel »
    box(x,y,w,130,"","white")
    text(x+w/2,y+12,"📄",30)
    text(x+w/2,y+55,s,16)
def users(x,y): box(x,y,90,60,"👥\nusers","white",16)

FW,FH,GAP=1300,860,120
def pos(i): return ( (i%2)*(FW+GAP), (i//2)*(FH+GAP) )

# ------------------------------------------------------------------ 1. VM unique
X,Y=frame(*pos(0),FW,FH,"1 · VM unique (A)")
title(X,Y,"1. Déployer l'application sur une seule VM (scénario A)","Tout est installé à la main sur la même machine")
users(X+40,Y+330); arrow(X+135,Y+360,X+215,Y+360)
group(X+220,Y+140,620,470,"VM Linux (8 vCPU, 16 Go)","grey")
box(X+250,Y+190,170,70,"vote\n(Python)","yellow",18); box(X+440,Y+190,170,70,"redis","red",18); box(X+630,Y+190,180,70,"worker\n(.NET)","violet",18)
box(X+250,Y+290,170,70,"result\n(Node.js)","green",18); box(X+440,Y+290,170,70,"db\n(PostgreSQL)","blue",18)
box(X+250,Y+400,560,60,"Python 3.11 · .NET · Node 20 · PostgreSQL 15 · Redis\ninstallés et configurés à la main","white",16)
box(X+250,Y+480,560,50,"système Linux (mises à jour, sécurité…)","white",16)
box(X+250,Y+545,560,45,"⚙️ démarrage : services systemd, scripts…","white",16)
doc(X+880,Y+140,"Manuel de déploiement\n~40 pages\n~150 commandes (fictif)",260)
note(X+880,Y+300,"📈 Scaling vertical : + CPU, + RAM\n→ facile (mais redémarrage, et une limite)",400)
note(X+880,Y+375,"↔️ Scaling horizontal : cloner la VM,\najouter un répartiteur de charge…\net la base de données ? → difficile",400)
note(X+880,Y+475,"💾 Sauvegarde : snapshot de la VM entière\n⚠️ Un seul point de défaillance",400)
# fantômes : ce qu'on « imagine »
box(X+220,Y+640,280,70,"VM 2 (réplique) ?","white",18,dashed=True,opacity=45)
box(X+560,Y+640,280,70,"Répartiteur de charge ?","white",18,dashed=True,opacity=45)
note(X+220,Y+725,"… et pour la haute disponibilité : réplication, bascule, sauvegardes, plan de reprise… à concevoir et à documenter",900,"#5c5f66",16)

# ------------------------------------------------------------------ 2. Plusieurs VM
X,Y=frame(*pos(1),FW,FH,"2 · Plusieurs VM (B)")
title(X,Y,"2. Plusieurs VM, plusieurs systèmes (scénario B, fictif)","Ex. : un ancien worker en .NET Framework impose un Windows Server")
users(X+40,Y+330); arrow(X+135,Y+360,X+195,Y+360)
group(X+200,Y+150,360,380,"VM Linux","grey")
box(X+230,Y+210,300,80,"vote (Python)","yellow",18); box(X+230,Y+320,300,80,"redis","red",18)
box(X+230,Y+430,300,70,"Python · Redis · systemd","white",16)
group(X+640,Y+150,400,480,"VM Windows Server","cyan")
box(X+670,Y+210,340,75,"worker (.NET Framework)","violet",18); box(X+670,Y+305,340,75,"db (PostgreSQL)","blue",18)
box(X+670,Y+400,340,75,"result (Node.js)","green",18); box(X+670,Y+500,340,100,".NET Framework · PostgreSQL\nNode.js · services Windows","white",16)
arrow(X+565,Y+360,X+665,Y+245,both=True)
note(X+560,Y+380,"10.0.0.12:6379",120,"#5c5f66",15)
doc(X+1065,Y+150,"Manuel Linux\n~25 pages",200)
doc(X+1065,Y+290,"Manuel Windows\n~35 pages",200)
note(X+200,Y+550,"🔌 Adresses IP écrites\nen dur entre les VM",420,size=17)
note(X+200,Y+605,"🛠️ Deux OS à patcher,\ndeux expertises",420,size=17)
note(X+1060,Y+440,"📈 Vertical : facile\n↔️ Horizontal : par VM,\nencore plus difficile\n💾 Snapshots ×2",230,size=17)
box(X+200,Y+680,300,60,"Répliques des VM ?","white",17,dashed=True,opacity=45)
box(X+540,Y+680,300,60,"Répartiteurs de charge ?","white",17,dashed=True,opacity=45)
note(X+880,Y+690,"… haute dispo, sauvegardes,\nplan de reprise ×2",360,"#5c5f66",16)

# ------------------------------------------------------------------ 3. Conteneurs A
X,Y=frame(*pos(2),FW,FH,"3 · Conteneurs (A)")
title(X,Y,"3. Conteneuriser : la même VM, un seul outil à installer (scénario A)","Docker + docker compose : le déploiement est standardisé")
box(X+300,Y+110,500,70,"🧊 Registre d'images (Docker Hub, ghcr.io, Harbor interne…)","violet",17)
arrow(X+550,Y+185,X+550,Y+240,label="pull")
users(X+40,Y+300); arrow(X+135,Y+330,X+245,Y+330)
group(X+220,Y+245,700,460,"VM Linux","grey")
box(X+250,Y+300,180,60,"reverse proxy","orange",17)
for i in range(3): box(X+470,Y+290+i*58,150,50,"vote","yellow",17)
arrow(X+430,Y+330,X+468,Y+315); arrow(X+430,Y+330,X+468,Y+373); arrow(X+430,Y+330,X+468,Y+431)
box(X+650,Y+290,120,50,"redis","red",17); box(X+780,Y+290,120,50,"worker","violet",17)
box(X+650,Y+360,120,50,"db","blue",17); box(X+780,Y+360,120,50,"result","green",17)
box(X+250,Y+500,650,60,"runtime de conteneurs (Docker) + docker compose : la SEULE chose à installer","white",16)
box(X+250,Y+580,650,50,"système Linux","white",16)
box(X+960,Y+250,300,140,"📄 compose.yml\n\ndocker compose up","white",18)
note(X+960,Y+410,"✅ Même paquet partout :\nnouvel OS, VM en plus,\nenvironnement de démo…\n→ installer le runtime, c'est tout",320,size=17)
note(X+960,Y+540,"📈 Vertical : toujours facile\n↔️ Horizontal : dupliquer\nles conteneurs (vote ×3)\n⚠️ … et gérer le routage",320,size=17)
note(X+220,Y+725,"Toujours une seule machine : si elle tombe, tout tombe.",900,"#5c5f66",17)

# ------------------------------------------------------------------ 4. Conteneurs B
X,Y=frame(*pos(3),FW,FH,"4 · Conteneurs (B)")
title(X,Y,"4. Conteneuriser le scénario B","Une fois en conteneurs, les composants Linux se regroupent")
box(X+350,Y+110,500,70,"🧊 Registre d'images partagé","violet",17)
arrow(X+520,Y+185,X+400,Y+245,label="pull"); arrow(X+680,Y+185,X+820,Y+245,label="pull")
group(X+120,Y+250,560,420,"VM Linux + runtime","grey")
box(X+150,Y+310,150,55,"vote","yellow",17); box(X+320,Y+310,150,55,"redis","red",17)
box(X+150,Y+390,150,55,"db","blue",17); box(X+320,Y+390,150,55,"result","green",17)
note(X+490,Y+320,"db et result\nn'ont plus besoin\nde Windows",180,"#2f9e44",16)
box(X+150,Y+480,500,55,"runtime de conteneurs + compose","white",16); box(X+150,Y+555,500,45,"Linux","white",16)
group(X+740,Y+250,440,420,"VM Windows Server + runtime","cyan")
box(X+780,Y+310,360,60,"worker (.NET Framework)","violet",17)
box(X+780,Y+480,360,55,"runtime (conteneurs Windows)","white",16); box(X+780,Y+555,360,45,"Windows Server","white",16)
arrow(X+685,Y+340,X+775,Y+340,label="réseau",both=True)
note(X+120,Y+690,"⚠️ Une image Linux ne tourne que sur un hôte Linux, une image Windows que sur un hôte Windows :\nla VM Windows reste nécessaire tant que le worker n'est pas porté en .NET moderne.",1060,"#e03131",17)
note(X+120,Y+760,"Deux machines, deux fichiers compose, le routage entre elles reste à gérer à la main.",1060,"#5c5f66",17)

# ------------------------------------------------------------------ 5. Le piège
X,Y=frame(*pos(4),FW,FH,"5 · Le piège")
title(X,Y,"5. Le piège : « j'installe Kubernetes comme un Docker de plus »","Un cluster d'un seul nœud, sur l'ancienne VM")
users(X+60,Y+370); arrow(X+155,Y+400,X+235,Y+400)
group(X+240,Y+150,640,560,"VM Linux = cluster d'UN nœud","grey")
box(X+270,Y+200,580,60,"plan de contrôle (API, ordonnanceur, etcd…)","violet",17)
for i in range(3): box(X+270+i*120,Y+290,105,50,"vote","yellow",16)
box(X+630,Y+290,105,50,"redis","red",16); box(X+745,Y+290,105,50,"worker","violet",16)
box(X+270,Y+360,105,50,"db","blue",16); box(X+390,Y+360,105,50,"result","green",16)
box(X+270,Y+440,580,55,"runtime de conteneurs (containerd)","white",16); box(X+270,Y+515,580,45,"Linux","white",16)
note(X+270,Y+590,"= docker compose… avec d'autres commandes",580,"#5c5f66",18)
note(X+920,Y+180,"✅ Gagné :\nauto-réparation des pods,\nmises à jour progressives,\nretour arrière, Services",340,"#2f9e44",18)
note(X+920,Y+360,"❌ Pas gagné :\ntoujours UNE machine\n→ pas de haute dispo,\nscaling limité à la VM",340,"#e03131",18)
note(X+920,Y+540,"Utile pour apprendre\n(c'est notre TP !),\npas pour la production.",340,"#1e1e1e",18)

# ------------------------------------------------------------------ 6. Les vraies décisions
X,Y=frame(*pos(5),FW,FH,"6 · Les vraies décisions")
title(X,Y,"6. Passer à un vrai cluster : les décisions à prendre","Exemple sur site : Rancher (open source, SUSE) + distribution RKE2")
box(X+40,Y+120,250,80,"🧭 Rancher\ngère le(s) cluster(s)","orange",17)
arrow(X+295,Y+160,X+355,Y+200,dashed=True)
group(X+360,Y+125,900,590,"Cluster RKE2","none")
box(X+390,Y+175,840,70,"plan de contrôle × 3 nœuds Linux (haute disponibilité)","violet",17)
group(X+390,Y+270,540,250,"pool de nœuds Linux × 3","grey")
for i,(n,c) in enumerate([("vote","yellow"),("vote","yellow"),("vote","yellow")]): box(X+410+i*170,Y+320,150,50,n,c,16)
box(X+410,Y+390,150,50,"redis","red",16); box(X+580,Y+390,150,50,"result","green",16); box(X+750,Y+390,150,50,"db","blue",16)
note(X+410,Y+460,"répartis par l'ordonnanceur",480,"#5c5f66",16)
group(X+950,Y+270,280,250,"nœud Windows","cyan")
box(X+970,Y+330,240,55,"worker","violet",16)
note(X+965,Y+400,"nodeSelector :\nkubernetes.io/os: windows",255,"#1e1e1e",15)
box(X+390,Y+545,260,60,"Ingress + LB","orange",16); box(X+680,Y+545,260,60,"Stockage (volumes)","blue",16); box(X+970,Y+545,260,60,"Sauvegardes (Velero)","green",16)
box(X+390,Y+630,840,60,"Registre interne (Harbor) · Supervision · Sécurité · Droits d'accès","white",16)
note(X+40,Y+240,"Les décisions :\n\n1. Comment créer le cluster ?\n   cloud managé, Rancher/RKE2,\n   OpenShift, Talos…\n2. Quelle topologie ?\n   HA, zones, nombre de nœuds\n3. Quel dimensionnement ?\n4. Linux et Windows ?\n   pools, affinités\n5. Les données ?\n   dans le cluster ou base managée\n6. Les anciennes VM ?\n   supprimées ou recyclées en nœuds",310,"#1e1e1e",16)
note(X+360,Y+735,"Le plan de contrôle est toujours sous Linux ; les nœuds Windows ne font que du « travail ».",900,"#5c5f66",16)

# ------------------------------------------------------------------ 7. Tableau
X,Y=frame(*pos(6),FW,FH,"7 · Récap")
title(X,Y,"7. Récapitulatif","Ce que chaque étape change")
cols=["","VM","Conteneurs\n(Docker, Compose)","Orchestrateur\n(Kubernetes)"]
rows=[("Déployer","manuel de 40 pages","« docker compose up »","« kubectl apply »,\nautomatisable (GitOps)"),
      ("Nouvel environnement\n(démo, recette…)","réinstaller tout","installer le runtime","un namespace\nou un cluster de plus"),
      ("Scaling vertical","facile","facile","réservations,\ntaille des nœuds"),
      ("Scaling horizontal","difficile\n(cloner, router)","sur une machine\n(+ routage)","natif : replicas\nsur plusieurs nœuds"),
      ("Panne","intervention\nhumaine","redémarrage\nlocal","réparation\nautomatique"),
      ("Haute disponibilité","à concevoir","à concevoir","native (si plusieurs\nnœuds)"),
      ("Coût d'entrée","faible","faible","élevé : compétences,\ninfra, outillage")]
cw=[280,290,300,330]; rh=82; x0=X+40; y0=Y+120
colors=["grey","red","yellow","green"]
for j,c in enumerate(cols):
    xx=x0+sum(cw[:j]); 
    if c: box(xx,y0,cw[j]-10,70,c,colors[j],18)
for i,r in enumerate(rows):
    yy=y0+80+i*(rh+8)
    for j,c in enumerate(r):
        xx=x0+sum(cw[:j])
        box(xx,yy,cw[j]-10,rh,c,"grey" if j==0 else "white",16)

doc_={"type":"excalidraw","version":2,"source":"https://github.com/bngams/kube-overview-labs","elements":els,
      "appState":{"viewBackgroundColor":"#ffffff","gridSize":None},"files":{}}
json.dump(doc_,open("recap-j1.excalidraw","w"),ensure_ascii=False,indent=1)
print(len(els),"éléments,", sum(1 for e in els if e['type']=='frame'),"cadres")
