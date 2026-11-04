/* Families pages: quick exit (button + Esc) and share. No tracking. */
(function(){
  function exit(){ try{document.body.innerHTML="";}catch(e){} location.replace("https://www.google.com.au"); }
  var q=document.getElementById("quick-exit"); if(q) q.addEventListener("click", exit);
  document.addEventListener("keydown", function(e){ if(e.key==="Escape" && !document.querySelector("dialog[open]")) exit(); });
  var s=document.getElementById("fam-share"), st=document.getElementById("fam-share-status");
  if(s) s.addEventListener("click", function(){
    var url=location.href.split("#")[0];
    if(navigator.share){ navigator.share({title:document.title,url:url}).catch(function(){}); return; }
    if(navigator.clipboard){ navigator.clipboard.writeText(url).then(function(){st.textContent="Link copied.";},function(){st.textContent=url;}); }
    else st.textContent=url;
  });
})();
