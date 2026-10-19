
const hdr=document.querySelector('.hdr');
const onScroll=()=>hdr.classList.toggle('solid',window.scrollY>60);
onScroll();addEventListener('scroll',onScroll,{passive:true});
const slides=[...document.querySelectorAll('.slide')],dots=[...document.querySelectorAll('.dot')];
let idx=0,timer=null;
function go(i){idx=(i+slides.length)%slides.length;
  slides.forEach((s,n)=>s.classList.toggle('on',n===idx));
  dots.forEach((d,n)=>d.classList.toggle('on',n===idx));}
function start(){if(slides.length>1&&!matchMedia('(prefers-reduced-motion: reduce)').matches){timer=setInterval(()=>go(idx+1),6500);}}
dots.forEach((d,n)=>d.addEventListener('click',()=>{clearInterval(timer);go(n);start();}));start();
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}}),{threshold:.14});
document.querySelectorAll('.rv').forEach(el=>io.observe(el));
setTimeout(()=>document.querySelectorAll('.rv:not(.in)').forEach(el=>el.classList.add('in')),2600);
const nums=[...document.querySelectorAll('[data-count]')];
const cio=new IntersectionObserver(es=>es.forEach(e=>{
  if(!e.isIntersecting)return;const el=e.target,target=+el.dataset.count;
  el.textContent='0';let t0=null;const dur=1100;
  const step=t=>{if(!t0)t0=t;const p=Math.min((t-t0)/dur,1);const v=target*(1-Math.pow(1-p,3));
    el.textContent=Math.round(v).toLocaleString('en-US');if(p<1)requestAnimationFrame(step);};
  requestAnimationFrame(step);cio.unobserve(el);
}),{threshold:.4});
nums.forEach(n=>cio.observe(n));
const f=document.querySelector('#inquiry');
if(f){f.addEventListener('submit',ev=>{ev.preventDefault();
  const d=new FormData(f),g=k=>(d.get(k)||'').toString().trim();
  const body=[`Name: ${g('name')}`,`Company: ${g('company')}`,`Email: ${g('email')}`,
    `Country: ${g('country')}`,`Substrate: ${g('substrate')}`,`Finish: ${g('finish')}`,
    `Volume: ${g('volume')}`,'',g('message')].join('\n');
  const to=f.dataset.email||'';
  if(to){location.href=`mailto:${to}?subject=${encodeURIComponent('Powder coating inquiry')}&body=${encodeURIComponent(body)}`;}
  const ok=document.querySelector('#formOk');ok.classList.add('on');
  ok.textContent=to?'Your email client should open with the inquiry filled in.':'Thank you. Please send the same details to the sales address listed in the footer.';
});}
