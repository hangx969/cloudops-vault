from pathlib import Path
from html import escape as E
import json,subprocess
OUT=Path('/Users/hang.xu/github-repo/cloudops-vault/Docker-Kubernetes/k8s-basic-resources/diagrams')
SK=Path('/Users/hang.xu/.codex/plugins/cache/diagram-design/diagram-design/2.6.120/skills/diagram-design')
STATE=Path('/private/tmp/k8s-basic-redraw-20261024/group-a.json')
P='#f7f9fc';I='#18263a';M='#4b5d75';A='#2458b6';T='#eaf1ff';R='#c8d3e2'
FONT="'Geist','Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif"
MONO="'Geist Mono','SFMono-Regular',monospace"
SERIF="'Instrument Serif','Noto Serif SC','Songti SC',serif"
LINK='https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;600&family=Noto+Serif+SC:wght@400&display=swap'
class D:
 def __init__(self,id,slug,title,kind,desc,note=''):
  self.id=id;self.slug='k8s-'+id+'-'+slug;self.title=title;self.kind=kind;self.desc=desc;self.note=note;self.z=[];self.e=[];self.l=[];self.n=[]
 def text(self,x,y,s,size=16,anchor='middle',color=I,weight=600,mono=False,serif=False):
  return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" font-family="{SERIF if serif else MONO if mono else FONT}" font-size="{size}" font-weight="{weight}">{E(s)}</text>'
 def zone(self,x,y,w,h,label):
  self.z.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#edf2f8" stroke="{R}" stroke-dasharray="4,4"/>'+self.text(x+16,y+24,label,14,'start',M))
 def node(self,x,y,w,h,name,sub='',focal=False,tag='',lines=None):
  s=A if focal else M;fill=T if focal else '#ffffff'
  q=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{P}"/><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{s}" stroke-width="1.2"/>'
  ls=lines or [name]
  if tag:q+=self.text(x+12,y+16,tag,8,'start',M,500,True)
  cy=y+h/2-(len(ls)-1)*10-(8 if sub else 0)+(4 if not tag else 8)
  for j,line in enumerate(ls):q+=self.text(x+w/2,cy+j*20,line)
  if sub:q+=self.text(x+w/2,y+h-12,sub,12,color=M,weight=400,mono=True)
  self.n.append(q)
 def arrow(self,pts,dash=False,accent=False,marker=True):
  # Round every orthogonal corner with radius 8, trimming to short segments.
  ss=f'M {pts[0][0]},{pts[0][1]}'
  for k in range(1,len(pts)-1):
   a,b,c=pts[k-1:k+2];d1=abs(b[0]-a[0])+abs(b[1]-a[1]);d2=abs(c[0]-b[0])+abs(c[1]-b[1]);r=min(8,d1/2,d2/2)
   pre=(b[0]+(a[0]-b[0])*r/d1,b[1]+(a[1]-b[1])*r/d1);post=(b[0]+(c[0]-b[0])*r/d2,b[1]+(c[1]-b[1])*r/d2)
   ss+=f' L {pre[0]},{pre[1]} Q {b[0]},{b[1]} {post[0]},{post[1]}'
  ss+=f' L {pts[-1][0]},{pts[-1][1]}'
  self.e.append(f'<path d="{ss}" fill="none" stroke="{A if accent else M}" stroke-width="1.2"'+(' stroke-dasharray="5,4"' if dash else '')+(f' marker-end="url(#arrow{ "-accent" if accent else ""})"' if marker else '')+'/>')
 def label(self,x,y,s,mono=False):
  import unicodedata
  w=8+sum(12 if unicodedata.east_asian_width(c) in 'WF' else 7.5 for c in s);w=int((w+3)//4*4)
  self.l.append(f'<rect x="{x-w/2}" y="{y-14}" width="{w}" height="20" rx="2" fill="{P}"/>'+self.text(x,y,s,12,color=M,weight=500,mono=mono))
 def save(self,notes):
  defs='<marker id="arrow-back" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto-start-reverse"><polygon points="0 0,8 3,0 6" fill="#4b5d75"/></marker>'+''.join(f'<marker id="arrow{suffix}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{col}"/></marker>' for suffix,col in [('',M),('-accent',A),('-link','#156273')])
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" role="img" aria-labelledby="{self.slug}-title {self.slug}-desc" data-size-preset="slide-16x9" data-detail="faithful"><title id="{self.slug}-title">{E(self.title)}</title><desc id="{self.slug}-desc">{E(self.desc)}</desc><defs>{defs}</defs><rect width="1280" height="720" fill="{P}"/>'+self.text(40,72,self.title,40,'start',I,400,serif=True)+self.text(40,108,self.kind,12,'start',M,400)+''.join(self.z+self.e+self.l+self.n)+f'<line x1="40" y1="652" x2="1240" y2="652" stroke="{R}"/>'+self.text(40,680,self.note,12,'start',M,400)+'</svg>'
  html=f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(self.title)}</title><link href="{LINK}" rel="stylesheet"><style>body{{margin:0;background:{P}}}.diagram-container{{width:100%;overflow-x:auto}}svg{{width:100%;min-width:1280px;display:block}}@media print{{.diagram-container{{overflow-x:visible}}svg{{min-width:0}}}}</style></head><body><div class="diagram-container">{svg}</div></body></html>'
  h=OUT/(self.slug+'.html');p=OUT/(self.slug+'.png');h.write_text(html)
  checks=[]
  for cmd in [['python3',str(SK/'scripts/self_check.py'),str(h)],['python3',str(SK/'scripts/export_png.py'),str(h),str(p),'2']]:
   r=subprocess.run(cmd,capture_output=True,text=True);checks.append({'command':Path(cmd[1]).name,'exit_code':r.returncode,'result':(r.stdout+r.stderr).strip()});print(self.id,checks[-1],flush=True)
   if r.returncode:raise RuntimeError(self.id)
  state=json.loads(STATE.read_text()) if STATE.exists() else []
  state=[x for x in state if x['id']!=self.id];state.append({'id':self.id,'classification':'diagram','status':'rendered','title':self.title,'visual_type':self.kind,'outputs':[{'html':str(h),'png':str(p)}],'fidelity_notes':notes,'checks':checks});STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2))

def one():
 d=D('01-01','cluster-architecture','Kubernetes 集群组件与工作节点','Architecture · 历史 Docker 实现','控制平面通过 API Server 协作，两个工作节点运行 kubelet、kube-proxy、Docker 与多个 Pod。','历史图保留 Docker；现代 kubelet 通过 CRI 调用运行时。kube-proxy 配置转发规则，不启动容器。')
 d.zone(40,196,400,420,'CONTROL PLANE / MASTER');d.zone(552,152,688,224,'WORKER NODE 1');d.zone(552,408,688,224,'WORKER NODE 2')
 d.node(96,136,272,64,'Kubernetes control');d.node(152,260,176,64,'API Server',focal=True)
 d.node(64,396,168,80,'controller-manager',lines=['controller-','manager']);d.node(264,396,152,80,'scheduler');d.node(152,528,176,64,'etcd','cluster')
 d.arrow([(232,200),(232,260)]);d.arrow([(148,396),(148,348),(196,348),(196,324)]);d.arrow([(340,396),(340,360),(280,360),(280,324)]);d.arrow([(248,324),(248,528)])
 for j,y in enumerate([152,408]):
  d.node(592,y+48,168,64,'kubelet');d.node(1016,y+48,184,64,'kube-proxy')
  d.zone(792,y+24,184,192,'DOCKER')
  d.node(808,y+72,152,64,'Pod 1',sub='3 containers');d.node(808,y+144,152,64,'Pod 2',sub='3 containers')
  d.arrow([(328,280+j*24),(480+j*24,280+j*24),(480+j*24,y+80),(592,y+80)])
  d.e[-1]=d.e[-1].replace(' marker-end=', ' marker-start="url(#arrow-back)" marker-end=')
  d.arrow([(760,y+64),(784,y+64),(784,y+104),(808,y+104)])
  d.arrow([(760,y+96),(776,y+96),(776,y+176),(808,y+176)])
  d.arrow([(1016,y+64),(992,y+64),(992,y+104),(960,y+104)])
  d.arrow([(1016,y+96),(1004,y+96),(1004,y+176),(960,y+176)])
 
 for k,caption in enumerate(['replication','namespace','serviceaccounts …']):d.n.append(d.text(148,492+k*16,caption,11,color=M,weight=400,mono=True))
 d.n.append(d.text(1108,136,'Internet',16));d.arrow([(1108,144),(1108,200)])
 d.save(['保留两个工作节点、每节点2个Pod且每Pod3个容器；重复容器以数量文字表达。','保留Docker历史运行时及控制组件职责；未将互联网到kube-proxy的线解释为进程流量经过kube-proxy。'])

def two():
 d=D('01-02','resource-relations','围绕 Pod 的 Kubernetes 资源关系','Architecture · 资源与所有权','Deployment 管理 ReplicaSet，CronJob 创建 Job，工作负载控制器管理 Pod，Pod 关联服务与卷。','实线：管理 / 创建；虚线：选择或挂载。PVC 是卷申请，ConfigMap 与 Secret 可作为卷的数据来源。')
 d.zone(40,152,1200,184,'POD CONTROLLERS')
 for x,name in [(208,'Deployment'),(608,'CronJob')]:d.node(x,184,184,64,name)
 for x,name in [(48,'DaemonSet'),(312,'ReplicaSet'),(576,'Job'),(840,'StatefulSet')]:d.node(x,272,184,64,name)
 d.arrow([(300,248),(300,260),(404,260),(404,272)]);d.arrow([(700,248),(700,260),(668,260),(668,272)])
 d.zone(432,400,416,112,'POD');d.node(452,436,176,64,'Container 1');d.node(652,436,176,64,'Container 2')
 for k,x in enumerate([140,404,668,932]):
  d.arrow([(x,336),(x,352+k*12),(480+k*88,352+k*12),(480+k*88,400)])
  if k==0:d.e[-1]=d.e[-1].replace('L 472.0,352.0','L 396,352 a 8,8 0 0,1 16,0 L 472.0,352.0')
 d.node(1000,428,216,64,'Service',focal=True);d.arrow([(1000,460),(848,460)],True)
 d.node(552,556,176,64,'Volume',focal=True);d.arrow([(640,512),(640,556)],True)
 for x,name in [(120,'ConfigMap'),(832,'PVC'),(1040,'Secret')]:
  d.node(x,556,160,64,name)
 d.arrow([(280,588),(552,588)],True);d.arrow([(832,576),(728,576)],True);d.arrow([(1120,620),(1120,636),(688,636),(688,620)],True)
 d.save(['保留六种控制器、两个容器、Service、Volume、ConfigMap、PVC、Secret全部原图对象。','原图Volume到三类配置/申请的关系改为带说明的挂载/数据来源，未将ConfigMap和Secret称为持久存储。'])

def pod_base():
 d=D('03-01','pod-sandbox','Pod：共享网络与独立应用容器','Architecture · Pod sandbox','同一 Pod 中的应用容器共享由 sandbox 维持的网络命名空间，分别运行 Nginx 与 Tomcat。','示例地址 192.168.1.1；pause 不计入 READY 容器数。共享文件需要容器显式挂载同一 Volume。')
 d.zone(120,164,1040,444,'POD · 共享 IP 与端口空间')
 d.node(184,232,384,112,'user container 1','user Image1 · nginx:80',tag='APPLICATION')
 d.node(712,232,384,112,'user container N','user ImageN · tomcat:8080',tag='APPLICATION')
 d.n.append(d.text(640,300,'…',16))
 d.node(328,456,624,96,'Pause / Infra container','gcr.io/google_containers/pause-amd64',focal=True,tag='HISTORICAL IMAGE')
 d.arrow([(376,456),(376,344)],True);d.arrow([(904,456),(904,344)],True)
 d.label(640,416,'维持共享的命名空间环境')
 d.save(['保留原图应用容器1到N、示例nginx 80、tomcat 8080、Pause镜像与示例IP。','保留历史镜像名作为示例，补入正文对sandbox及卷共享的边界说明。'])

def sync():
 d=D('03-02','git-sync-sidecar','同一 Pod 内协作：文件同步','Architecture · Sidecar','Go 业务容器与定时 Git 同步容器挂载共享卷，业务容器读取同步后的文件。','同步文件是否立即生效取决于应用加载方式；更新源码不会自动替换正在运行的 Go 二进制。')
 d.zone(160,176,960,416,'POD')
 d.node(224,264,304,96,'Go 业务容器','application');d.node(752,264,304,96,'定时同步 Git 代码','sidecar / git-sync',focal=True)
 d.node(468,456,344,88,'共享 Volume','explicit volumeMounts')
 d.arrow([(904,360),(904,500),(812,500)]);d.arrow([(468,500),(376,500),(376,360)])
 d.label(940,416,'写入文件');d.label(340,416,'读取文件')
 d.save(['保留原图Pod内Go和Git同步两个组件。','共享卷来自紧邻正文；显式补出文件传递路径，并保留不等同于自动升级的限制。'])

def logs():
 d=D('03-03','logging-sidecar','同一 Pod 内协作：日志采集','Architecture · Sidecar','业务容器将日志写入共享卷，日志采集容器读取后发送到统一日志服务。','两个容器挂载同一个 Volume 才能共享日志文件；日志收集逻辑与业务代码分离。')
 d.zone(40,180,808,412,'POD')
 d.node(80,268,264,88,'核心业务容器','application');d.node(544,268,264,88,'日志收集服务','collector sidecar',focal=True)
 d.node(208,460,472,88,'共享日志目录','access.log · error.log · warning.log · info.log')
 d.node(952,268,288,88,'Logging Server','central logging')
 d.arrow([(212,356),(212,408),(336,408),(336,460)]);d.arrow([(552,460),(552,408),(676,408),(676,356)]);d.arrow([(808,312),(952,312)])
 d.label(272,394,'写入');d.label(616,394,'读取');d.label(880,284,'发送日志')
 d.save(['保留核心业务、日志收集服务、统一logging Server与4种日志文件。','原图未显式画卷，依据相邻正文把文件共享条件画成Volume。'])

def seq():
 d=D('03-04','pod-create-sequence','Pod 创建：用户提交与 API 持久化','Sequence · 创建流程 1 / 3','用户提交 Pod 后，API Server 将对象写入 etcd，并返回请求已接受。','API 接受对象不代表容器已运行；调度与启动见下一张图。实线为请求，虚线为返回。')
 for name,x in [('用户',256),('API Server',640),('etcd',1024)]:
  d.node(x-100,176,200,64,name)
  d.z.append(f'<line x1="{x}" y1="240" x2="{x}" y2="600" stroke="{R}" stroke-dasharray="3,3"/>')
 for a,b,y,s,ds in [(256,640,304,'CREATE POD',False),(640,1024,380,'WRITE',False),(1024,640,456,'RETURN',True),(640,256,532,'ACCEPTED',True)]:
  d.arrow([(a,y),(b,y)],ds);d.label((a+b)/2,y-14,s,True)
 d.save(['保留原图用户提交、API写入etcd、etcd返回及API接受响应4条消息。','原图拆为3张连续时序图，每张不超过5条生命线。'])
 d=D('03-04a','pod-scheduling-startup','Pod 创建：调度绑定与容器启动','Sequence · 创建流程 2 / 3','调度器观察未调度 Pod 并提交绑定，kubelet 观察绑定后用 Docker 启动容器。','历史图保留 Docker / docker run；现代 kubelet 经 CRI 调用运行时。观察变化经 API Server，不直接写 etcd。')
 for name,x in [('API Server',128),('etcd',384),('Scheduler',640),('kubelet',896),('Docker',1152)]:
  d.node(x-88,152,176,64,name)
  d.z.append(f'<line x1="{x}" y1="216" x2="{x}" y2="620" stroke="{R}" stroke-dasharray="3,3"/>')
 msgs=[(128,640,252,'WATCH: NEW',False,480),(640,128,300,'BIND POD',False,480),(128,384,348,'WRITE',False,256),(384,128,396,'RETURN',True,256),(128,640,444,'RETURN',True,480),(128,896,492,'WATCH: BOUND',False,512),(896,1152,540,'DOCKER RUN',False,1024),(1152,896,588,'RETURN',True,1024)]
 for a,b,y,s,ds,lx in msgs:d.arrow([(a,y),(b,y)],ds);d.label(lx,y-14,s,True)
 d.save(['保留调度器观察、绑定、etcd写入/返回、API向调度器返回、kubelet观察、Docker调用及返回8条消息。','保留原图Docker历史实现与顺序，5条生命线。'])
 d=D('03-04b','pod-status-persistence','Pod 状态更新与持久化','Sequence · 创建流程 3 / 3','kubelet 将 Pod 状态更新提交 API Server，后者写入 etcd 并返回。','续接上一张图容器启动结果；组件通过 API Server 协作，不直接写 etcd。')
 for n,x in [('kubelet',256),('API Server',640),('etcd',1024)]:
  d.node(x-100,176,200,64,n);d.z.append(f'<line x1="{x}" y1="240" x2="{x}" y2="600" stroke="{R}" stroke-dasharray="3,3"/>')
 for a,b,y,s,ds in [(256,640,304,'UPDATE STATUS',False),(640,1024,380,'WRITE',False),(1024,640,456,'RETURN',True),(640,256,532,'RETURN',True)]:d.arrow([(a,y),(b,y)],ds);d.label((a+b)/2,y-14,s,True)
 d.save(['保留原图update pod status、etcd写入及双返回4条消息。'])
 state=json.loads(STATE.read_text());main=next(x for x in state if x['id']=='03-04')
 main['title']='Pod 创建：提交、调度启动与状态持久化'
 for sid in ['03-04a','03-04b']:
  part=next(x for x in state if x['id']==sid);main['outputs']+=part['outputs'];main['checks']+=part['checks'];main['fidelity_notes']+=part['fidelity_notes']
 state=[x for x in state if x['id'] not in ['03-04a','03-04b']];STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2))

def lifecycle():
 d=D('03-05','pod-lifecycle','Pod 生命周期：初始化、运行与终止','Timeline · 阶段示意（非严格时序）','普通初始化容器依次完成，应用容器启动后执行生命周期钩子与健康探针，终止时调用 PreStop。','PostStart 与入口程序无先后保证；Liveness / Readiness 无固定先后。横轴只表示阶段，不表示持续时间。')
 # Relative stage lengths deliberately not a quantitative axis.
 rows=[(152,80,160,'Init container 1',False),(212,240,160,'Init container 2',False),(272,400,160,'Init container 3',False),(332,584,176,'PostStart',False),(392,584,616,'Main container',True),(452,784,304,'Liveness probe',False),(512,784,304,'Readiness probe',False),(572,1104,96,'PreStop',False)]
 for y,x,w,n,f in rows:d.node(x,y,w,48,n,focal=f)
 for x in [568,776,1096]:d.z.append(f'<line x1="{x}" y1="144" x2="{x}" y2="632" stroke="{R}" stroke-dasharray="4,4"/>')
 d.l.append(d.text(296,632,'普通 Init 顺序完成',12,color=M,weight=400));d.l.append(d.text(936,632,'若配置 Startup Probe，成功后才开始 Liveness / Readiness',12,color=M,weight=400))
 d.save(['保留原图3个普通Init、PostStart、main container、liveness、readiness、PreStop全部阶段。','采用阶段条形而非精确时间比例；根据相邻正文加入Startup Probe和非严格先后注释。'])

def rolling():
 d=D('07-01','rolling-update','Deployment 滚动更新：旧副本逐步替换','Architecture · 四个连续快照','Deployment 管理新旧 ReplicaSet，逐步增加 v2 Pod 并终止 v1 Pod，最终全部使用 v2。','每个快照保留 3 个 Pod 槽位；带斜杠的旧 Pod 正在移除。实际增减数量受 maxSurge / maxUnavailable 约束。')
 for k in range(4):
  x=40+k*304;d.zone(x,152,288,456,f'STEP {k+1:02d}')
  d.node(x+64,524,160,64,'Deployment')
  d.node(x+16,400,120,64,'ReplicaSet','template:v1');d.node(x+152,400,120,64,'ReplicaSet','template:v2',focal=k==3)
  d.arrow([(x+104,524),(x+104,496),(x+76,496),(x+76,464)]);d.arrow([(x+184,524),(x+184,496),(x+212,496),(x+212,464)])
  for j in range(3):
   px=x+16+j*88;ver=1 if j<3-k else 2;d.node(px,248,80,64,f'v{ver}')
   src=x+76 if ver==1 else x+212
   port=src+(-24+j*16 if ver==1 else -16+j*16)
   d.arrow([(port,400),(port,352+j*12),(px+40,352+j*12),(px+40,312)])
   if j==2-k and k<3:
    d.n.append(f'<path d="M {px+12},260 L {px+68},300" stroke="{M}" stroke-width="1.2"/>')
 d.save(['保留四个快照、每快照Deployment及新旧ReplicaSet、3个Pod槽位，合计24主节点。','原图带叉的终止Pod以单斜杠标记；保留新旧副本增减方向。'])

def bluegreen(id,active):
 title='蓝绿部署：'+('切换前流量进入旧版' if active==1 else '切换后流量进入新版')
 d=D(id,'blue-green-'+('before' if active==1 else 'after'),title,'Architecture · 两套运行环境',title+'，两个环境均保留 App1、App2、App3 与 App2 数据库。','绿色 / 蓝色为原图环境名称；同一蓝色主题通过版本标签区分环境。入口切换不会撤销已经发生的数据写入。')
 d.node(72,324,192,96,'Reverse proxy','traffic entry',focal=True)
 for j,(lab,ver) in enumerate([('绿色环境 · 旧版','v1'),('蓝色环境 · 新版','v2')]):
  y=160+j*248;d.zone(424,y,800,216,lab)
  for xx,n in [(464,'App1'),(704,'App2'),(944,'App3')]:d.node(xx,y+56,200,64,n,ver)
  d.node(704,y+140,200,64,'DB','App2 database')
  d.arrow([(804,y+120),(804,y+140)])
  if j+1==active:d.arrow([(264,372),(344,372),(344,y+88),(424,y+88)])
 d.label(380,328 if active==1 else 416,'当前流量')
 d.save(['保留反向代理、两套环境的App1/App2/App3以及各自App2关联DB。','原图绿色/蓝色环境颜色以明确名称和v1/v2代替，遵守统一Kubernetes蓝色主题。'])

def canary():
 d=D('07-04','canary-release','金丝雀发布：按比例验证新版本','Architecture · 流量分配示例','用户请求由路由器分为95%旧版本与5%新版本，每个版本保留Web、Application和Database三层。','95% / 5% 是原图示例比例；实际流量比例需由具备权重路由能力的入口实现。')
 d.node(40,324,152,80,'Users');d.node(264,324,152,80,'Router',focal=True);d.arrow([(192,364),(264,364)])
 for j,(v,pc) in enumerate([('Old Version','95%'),('New Version','5%')]):
  y=176+j*248;d.zone(568,y,672,176,v)
  for xx,ns in [(600,['Web','Server']),(824,['Application','Server']),(1048,['Database','Server'])]:d.node(xx,y+64,160,80,'',lines=ns)
  d.arrow([(760,y+104),(824,y+104)]);d.arrow([(984,y+104),(1048,y+104)])
  d.arrow([(416,348+j*32),(488+j*24,348+j*32),(488+j*24,y+104),(600,y+104)])
  d.label(504 if j==0 else 544,y+76,pc,True)
 d.save(['保留Users、Router、95%旧版本、5%新版本以及每套Web/Application/Database三层。'])

def job():
 d=D('09-01','job-restart-policy','Job：进程退出与失败重试','State machine · 三条任务执行路径','退出码0表示容器正常结束；Never不在原Pod重启，OnFailure允许在同一Pod中重试失败容器。','Completed 常对应 Pod Succeeded；某个 Pod 失败不等于 Job 立即失败，控制器还受 backoffLimit 等限制。')
 for y,policy in [(168,'正常退出'),(324,'restartPolicy: Never'),(480,'restartPolicy: OnFailure')]:d.z.append(d.text(40,y+24,policy,14,'start',M))
 d.node(328,152,256,80,'Pod / container','exit 0');d.node(904,152,296,80,'Completed','Pod Succeeded',focal=True);d.arrow([(584,192),(904,192)])
 d.node(328,308,256,80,'Pod / container','exit != 0');d.node(904,308,296,80,'Pod 失败','no in-place restart');d.arrow([(584,348),(904,348)])
 d.node(328,464,256,80,'Pod / container','exit != 0');d.node(664,464,192,80,'容器重启','same Pod');d.node(944,464,256,80,'Completed','then exit 0');d.arrow([(584,504),(664,504)]);d.arrow([(856,504),(944,504)])
 d.label(624,476,'失败重试');d.label(900,476,'成功退出')
 d.save(['保留原图exit0、Never失败、OnFailure失败后重启并成功三条路径。','原图Failure可能被误读为Job立即失败，按相邻正文明确为Pod失败，并保留Job重试边界提示。'])

def sts():
 d=D('14-01','statefulset-storage','StatefulSet：每个序号持有自己的卷','Architecture · Pod / PVC / PV','StatefulSet从Pod模板生成有序Pod，从卷申请模板生成每个序号的PVC并分别绑定PV。','图中沿用原图 web-0 / web-1；正文实例 sts-web 的 PVC 名称为 www-sts-web-0、www-sts-web-1。')
 d.zone(40,168,312,436,'STATEFULSET')
 d.node(72,248,248,80,'Pod template');d.node(72,456,248,88,'volumeClaimTemplates',focal=True)
 for j,y in enumerate([248,456]):
  d.node(456,y,184,80,'Pod',f'web-{j}');d.node(768,y,216,80,'PVC',f'web-{j}');d.node(1088,y,152,80,'PV',f'volume {j}')
  d.arrow([(640,y+40),(768,y+40)]);d.arrow([(984,y+40),(1088,y+40)])
 d.arrow([(320,272),(456,272)]);d.arrow([(320,304),(384,304),(384,480),(456,480)])
 d.arrow([(320,504),(408,504),(408,392),(876,392),(876,328)])
 d.e[-1]=d.e[-1].replace('L 408.0,400.0','L 408,488 a 8,8 0 0,1 0,-16 L 408.0,400.0')
 d.arrow([(320,524),(384,524),(384,584),(876,584),(876,536)])
 d.label(1028,260,'绑定');d.label(1028,468,'绑定')
 d.save(['保留StatefulSet、Pod template、volumeClaimTemplates以及两组Pod/PVC/PV对应关系。','保留原图web-0/web-1简写，脚注对应正文sts-web与完整PVC名称。'])

def exclusions():
 st=json.loads(STATE.read_text()) if STATE.exists() else []
 for id,why in [('02-01','kubectl explain pod.spec.containers 的CLI输出与字段注释截图，非示意图。'),('02-02','YAML字段名与中文含义的纯表格截图，没有架构、流程或资源关系。')]:
  st=[x for x in st if x['id']!=id];st.append({'id':id,'classification':'screenshot','status':'excluded','title':'字段说明截图','visual_type':None,'outputs':[],'fidelity_notes':[],'checks':['已逐张查看原图并结合相邻正文判定。'],'excluded_reason':why})
 STATE.write_text(json.dumps(st,ensure_ascii=False,indent=2))

if __name__=='__main__':
 import sys
 fun={'01-01':one,'01-02':two,'03-01':pod_base,'03-02':sync,'03-03':logs,'03-04':seq,'03-05':lifecycle,'07-01':rolling,'07-02':lambda:bluegreen('07-02',1),'07-03':lambda:bluegreen('07-03',2),'07-04':canary,'09-01':job,'14-01':sts}
 exclusions()
 for id in sys.argv[1:] or fun:fun[id]()
