import{E as g}from"./element-plus-Dyxpokyy.js";import{_ as k}from"./index-cP0Ss04Y.js";import{k as i,M as t,P as l,a0 as r,F as y,ae as V,W as d,Z as C,c as A,aj as c,L as s,$ as N,_ as m}from"./vue-vendor-BlNVQWYY.js";import"./axios-DBRE6jjL.js";const B={class:"page-card"},D={class:"disclaimer-box"},E={class:"mt16"},I={key:0,style:{"margin-left":"12px",color:"#67C23A","font-size":"13px"}},S={__name:"Disclaimer",setup(w){const a=i(!1),n=i(localStorage.getItem("disclaimerAccepted")==="1"),p=A(()=>`本平台提供的客户大数据采集与分析服务，旨在帮助用户合法合规地开展市场调研与客户开发工作。
使用本平台前，请您仔细阅读并理解以下条款：

一、合法性声明
1. 本平台采集的数据来源于互联网公开信息，仅限用于合法的商业调研、客户服务与市场分析用途。
2. 用户承诺：不得将本平台数据用于骚扰、诈骗、侵犯个人隐私、不正当竞争或其他任何违法违规活动。
3. 涉及个人信息的数据，用户应遵守《中华人民共和国个人信息保护法》《中华人民共和国数据安全法》及《中华人民共和国网络安全法》等相关法律法规。

二、使用限制
1. 禁止利用本平台对任何平台进行恶意攻击、高频抓取、绕过风控等破坏性行为。
2. 禁止将线索数据出售、转售或提供给任何第三方用于非法用途。
3. 用户应合理控制采集频率，尊重各平台的服务协议与 robots 协议。

三、数据合规
1. 本平台对采集的数据执行 30 天自动清理机制，到期数据将自动删除。
2. 本平台记录全部操作日志与采集日志，留存备查。
3. 用户应对自身账号下的所有操作行为负责。

四、免责声明
1. 因用户违规使用本平台导致的法律责任，由用户自行承担。
2. 本平台不保证数据的完整性、准确性或时效性，数据仅供参考。
3. 本平台不对因使用数据产生的任何直接或间接损失承担责任。

五、其他
1. 本声明解释权归本平台所有，平台有权根据法律法规变化适时更新本声明。
2. 继续使用本平台即视为您已阅读并同意本声明的全部内容。`.split(`
`)),u=()=>{localStorage.setItem("disclaimerAccepted","1"),n.value=!0,g.success("已确认同意，感谢您的配合")};return(_,e)=>{const f=c("el-alert"),v=c("el-checkbox"),x=c("el-button");return s(),t("div",B,[e[3]||(e[3]=l("div",{class:"page-title"},"合规与免责声明",-1)),r(f,{type:"warning",closable:!1,class:"mb16",title:"本平台仅用于合法合规的商业调研与客户开发，禁止用于骚扰、诈骗、侵犯隐私等违法用途。"}),l("div",D,[(s(!0),t(y,null,V(p.value,(o,b)=>(s(),t("p",{key:b,class:"disclaimer-line"},N(o),1))),128))]),l("div",E,[r(v,{modelValue:a.value,"onUpdate:modelValue":e[0]||(e[0]=o=>a.value=o)},{default:d(()=>[...e[1]||(e[1]=[m("我已仔细阅读并同意以上声明全部内容",-1)])]),_:1},8,["modelValue"])]),r(x,{type:"primary",class:"mt16",disabled:!a.value,onClick:u},{default:d(()=>[...e[2]||(e[2]=[m("确认并同意",-1)])]),_:1},8,["disabled"]),n.value?(s(),t("span",I,"✓ 已同意")):C("",!0)])}}},z=k(S,[["__scopeId","data-v-e5b807e1"]]);export{z as default};
