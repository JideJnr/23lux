const config=window.BOOKING_CONFIG;
const ready=config?.url?.startsWith('https://')&&config?.key;
async function api(path,options={},token){
 const response=await fetch(`${config.url}${path}`,{...options,headers:{apikey:config.key,'Content-Type':'application/json',...(token?{Authorization:`Bearer ${token}`} : {}),...options.headers}});
 const body=await response.json().catch(()=>null);
 if(!response.ok)throw new Error('The request could not be completed. Please try again or contact the studio.');
 return body;
}
const form=document.querySelector('#booking-form');
if(form){
 const service=form.querySelector('#service'),price=document.querySelector('#service-price'),submit=form.querySelector('[type=submit]'),status=document.querySelector('#booking-status');
 function updatePrice(){const item=window.SERVICES.find(s=>s.id===service.value);price.textContent=item?`${item.price===null?'Price on consultation':new Intl.NumberFormat('en-NG',{style:'currency',currency:'NGN',maximumFractionDigits:0}).format(item.price)} · base service price; extras confirmed with the studio.`:'';}
 service.replaceChildren(...window.SERVICES.map(s=>{const o=document.createElement('option');o.value=s.id;o.textContent=s.name;return o;}));service.onchange=updatePrice;updatePrice();
 document.querySelectorAll('[data-service]').forEach(link=>link.addEventListener('click',()=>{service.value=window.SERVICES.find(s=>s.category===link.dataset.service)?.id||service.value;updatePrice();}));
 if(!ready){submit.disabled=true;status.textContent='Online booking is being set up. Please use WhatsApp to request an appointment for now.';}
 let requestId=crypto.randomUUID();form.addEventListener('input',()=>{requestId=crypto.randomUUID();});
 form.addEventListener('submit',async event=>{event.preventDefault();if(!ready)return;submit.disabled=true;status.textContent='Sending your booking request…';const data=new FormData(form);try{
 const result=await api('/rest/v1/rpc/request_booking',{method:'POST',body:JSON.stringify({p_request_id:requestId,p_name:data.get('name').trim(),p_phone:data.get('phone').trim(),p_service:service.value,p_preferred_at:`${data.get('date')}T${data.get('time')}:00+01:00`,p_notes:data.get('notes').trim(),p_website:data.get('website')})});
 status.textContent=`Request received. Reference: ${result}. The studio will contact you to confirm your appointment. Your requested time is not reserved yet.`;
 const link=document.querySelector('#booking-whatsapp');link.href=`https://wa.me/2348026676582?text=${encodeURIComponent(`Hi 23 Lux Nails! I submitted booking request ${result} for ${service.selectedOptions[0].textContent}. I'd like to continue our conversation here.`)}`;link.hidden=false;form.hidden=true;
 }catch(error){status.textContent=error.message+' No confirmation has been received; please retry the same request.';submit.disabled=false;}});
}
