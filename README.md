## Chatellite 🛰

It's hard to look anywhere these days without hearing about how ChatGPT will be a solution to _$thing_.

In my day job at [ICEYE](https://www.iceye.com), I'm part of a team writing software that helps track our satellites. The 1st of April was coming up and it felt like too good an opportunity to miss, and so, behold [chatellite](https://chatellite.space).

Whilst it was certainly interesting to kick the tyres of LLMs, for me, the itch I'd been wanting to scratch for a while was 'how can one go from Lat/Lon point, to human-understandable place name'.
It turns out one way this can be done is to download the polygons at a chosen scale from [Natural Earth Data](https://www.naturalearthdata.com/) - and using GeoPandas we can do an `sjoin` to find which polgon a point, or set of points, would intersect with.

My goal for this was to be able to have reasonably recognisable place names to an English speaking international audience, so 'California, USA' was in, but 'Rutland, United Kingdom' would be 'too much info.' for this. So I was just about able to mash together the 'Admin 0 Counties' and 'Admin 1, States, provinces' from the 1:50m cultural vectors of Natural Earth, using QGis. I have absolutely no experience in this and the bundled ZIP file in this repo (I know, I know) is sufficiently terrible. But it was all good fun. Also my Front End skills leave a lot to be desired. But if it's stupid (and make no mistake - this is), and it works, then...


It goes without saying, this was intended purely as a bit of fun, it does not represent anything my employer may or may not think, absolutely no liability is accepted - and this was done in the evenings around life and work, so shortcuts were taken.
