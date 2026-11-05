/* HomeCircle share card. No network, no analytics. */
(function(){
  var s=document.getElementById("hc-share"), st=document.getElementById("hc-share-status");
  if(!s) return;
  s.addEventListener("click", function(){
    var url=location.origin+"/";
    if(navigator.share){ navigator.share({title:"HomeCircle: free recovery support in Australia",text:"HomeCircle is free recovery support in Australia: meetings, breathing tools, the 12 Steps and helplines. Support, not medical care.",url:url}).catch(function(){}); return; }
    if(navigator.clipboard){ navigator.clipboard.writeText(url).then(function(){st.textContent="Link copied. Paste it anywhere.";},function(){st.textContent=url;}); }
    else st.textContent=url;
  });
})();
