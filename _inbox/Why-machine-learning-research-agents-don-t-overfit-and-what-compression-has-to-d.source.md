---
source_url: https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit
fetched_at: 2026-09-17T01:09:59Z
fetch_method: jina
issue: 320
author: https://www.amazon.science/author/martin-bertran-lopez
published_at: 2026-09-10
cover_image: https://cdn.amazon.science/dims4/default/8f33283/2147483647/strip/true/crop/1920x1008+0+36/resize/1200x630!/quality/90/?url=https%3A%2F%2Famzn-science-production-science.s3.us-east-1.amazonaws.com%2Fscience%2F28%2F46%2F0121ba1e4b42be0c56e7560c9844%2Fcompressionmodels-03-16x9.png
title_zh: 机器学习研究 Agent 为什么不过拟合？
tech_domain: ai
---

# Why machine learning research agents don't overfit — and what compression has to do with it - Amazon Science

*   
[

<!-- media:svg src="https://cdn.amazon.science/ce/51/a0ecec814b0894e11c0f22dbcc17/amazonscience-white.svg" -->

<!-- media:svg src="https://cdn.amazon.science/fb/1c/07d25693486eb3d6b49091864af7/amazonscience-squidink.svg" -->

Research](https://www.amazon.science/research-areas)  
    *   Research
    *   
Research areas
        *   [![Image 1: Automated reasoning.svg](https://cdn.amazon.science/7c/fb/3a915dcf44b3ae2cac79acf280d8/automated-reasoning.svg)Automated reasoning](https://www.amazon.science/research-areas/automated-reasoning)
        *   [![Image 2: Reduced padding - Research areas](https://cdn.amazon.science/26/0a/47bb5de4438483f43551f13963d9/cloud-and-systems.svg)Cloud and systems](https://www.amazon.science/research-areas/cloud-and-systems)
        *   [![Image 3: Reduced padding - Research areas](https://cdn.amazon.science/6a/16/a6e53bfe46ceab77d292a8cea6af/computer-vision.svg)Computer vision](https://www.amazon.science/research-areas/computer-vision)
        *   [![Image 4: Reduced padding - Research areas](https://cdn.amazon.science/2e/8b/017e23db42f0a6e2c4e12a24f2aa/conversational-ai-and-natural-language-processing.svg)Conversational AI](https://www.amazon.science/research-areas/conversational-ai-natural-language-processing)
        *   [![Image 5: Reduced padding - Research areas](https://cdn.amazon.science/c3/a9/4eaa12b34e018438b648da0984c8/economics.svg)Economics](https://www.amazon.science/research-areas/economics)
        *   [![Image 6: Reduced padding - Research areas](https://cdn.amazon.science/8e/8b/3f08e7fd495c9f3ca8667d280825/information-and-knowledge-management.svg)Information and knowledge management](https://www.amazon.science/research-areas/information-and-knowledge-management)
        *   [![Image 7: Reduced padding - Research areas](https://cdn.amazon.science/9b/85/f1a70d944530ab25b4100eca8ae6/machine-learning.svg)Machine learning](https://www.amazon.science/research-areas/machine-learning)
        *   [![Image 8: Reduced padding - Research areas](https://cdn.amazon.science/af/26/afe9cd8041779f0d098ccd7cc686/operations-research-and-optimization.svg)Operations research and optimization](https://www.amazon.science/research-areas/operations-research-and-optimization)
        *   [![Image 9: Reduced padding - Research areas](https://cdn.amazon.science/30/fa/d9b66fce484290127e3e4319f45e/quantum-technologies.svg)Quantum technologies](https://www.amazon.science/research-areas/quantum-technologies)
        *   [![Image 10: Reduced padding - Research areas](https://cdn.amazon.science/5d/b0/310093db4e0da3496b9bac97b17f/robotics.svg)Robotics](https://www.amazon.science/research-areas/robotics)
        *   [![Image 11: Reduced padding - Research areas](https://cdn.amazon.science/91/f9/abec27f74777b60a69e3e4280228/search-and-information-retrieval.svg)Search and information retrieval](https://www.amazon.science/research-areas/search-and-information-retrieval)
        *   [![Image 12: Security privacy and abuse prevention (1).png](https://cdn.amazon.science/dims4/default/661340e/2147483647/strip/true/crop/180x180+0+0/resize/21x21!/quality/90/?url=https%3A%2F%2Famzn-science-production-science.s3.us-east-1.amazonaws.com%2Fscience%2Fab%2F95%2F437c6e1d42a9864318f0a9ea4142%2Fsecurity-privacy-and-abuse-prevention-1.png)Security, privacy, and abuse prevention](https://www.amazon.science/research-areas/security-privacy-and-abuse-prevention)
        *   [![Image 13: Reduced padding - Research areas](https://cdn.amazon.science/fc/ba/b7df3c284e6b9afc3487753a1bad/sustainability.svg)Sustainability](https://www.amazon.science/research-areas/sustainability)

    *   
Our scientific contributions
        *   [Publications Research from our scientists and collaborators.](https://www.amazon.science/publications) 
        *   [Conferences Our experts present and discuss cutting-edge research at scientific meetings globally.](https://www.amazon.science/conferences-and-events) 

    *   
Research areas
        *   [![Image 14: Automated reasoning.svg](https://cdn.amazon.science/7c/fb/3a915dcf44b3ae2cac79acf280d8/automated-reasoning.svg)Automated reasoning](https://www.amazon.science/research-areas/automated-reasoning)
        *   [![Image 15: Reduced padding - Research areas](https://cdn.amazon.science/26/0a/47bb5de4438483f43551f13963d9/cloud-and-systems.svg)Cloud and systems](https://www.amazon.science/research-areas/cloud-and-systems)
        *   [![Image 16: Reduced padding - Research areas](https://cdn.amazon.science/6a/16/a6e53bfe46ceab77d292a8cea6af/computer-vision.svg)Computer vision](https://www.amazon.science/research-areas/computer-vision)
        *   [![Image 17: Reduced padding - Research areas](https://cdn.amazon.science/2e/8b/017e23db42f0a6e2c4e12a24f2aa/conversational-ai-and-natural-language-processing.svg)Conversational AI](https://www.amazon.science/research-areas/conversational-ai-natural-language-processing)
        *   [![Image 18: Reduced padding - Research areas](https://cdn.amazon.science/c3/a9/4eaa12b34e018438b648da0984c8/economics.svg)Economics](https://www.amazon.science/research-areas/economics)
        *   [![Image 19: Reduced padding - Research areas](https://cdn.amazon.science/8e/8b/3f08e7fd495c9f3ca8667d280825/information-and-knowledge-management.svg)Information and knowledge management](https://www.amazon.science/research-areas/information-and-knowledge-management)
        *   [![Image 20: Reduced padding - Research areas](https://cdn.amazon.science/9b/85/f1a70d944530ab25b4100eca8ae6/machine-learning.svg)Machine learning](https://www.amazon.science/research-areas/machine-learning)
        *   [![Image 21: Reduced padding - Research areas](https://cdn.amazon.science/af/26/afe9cd8041779f0d098ccd7cc686/operations-research-and-optimization.svg)Operations research and optimization](https://www.amazon.science/research-areas/operations-research-and-optimization)
        *   [![Image 22: Reduced padding - Research areas](https://cdn.amazon.science/30/fa/d9b66fce484290127e3e4319f45e/quantum-technologies.svg)Quantum technologies](https://www.amazon.science/research-areas/quantum-technologies)
        *   [![Image 23: Reduced padding - Research areas](https://cdn.amazon.science/5d/b0/310093db4e0da3496b9bac97b17f/robotics.svg)Robotics](https://www.amazon.science/research-areas/robotics)
        *   [![Image 24: Reduced padding - Research areas](https://cdn.amazon.science/91/f9/abec27f74777b60a69e3e4280228/search-and-information-retrieval.svg)Search and information retrieval](https://www.amazon.science/research-areas/search-and-information-retrieval)
        *   [![Image 25: Security privacy and abuse prevention (1).png](https://cdn.amazon.science/dims4/default/661340e/2147483647/strip/true/crop/180x180+0+0/resize/21x21!/quality/90/?url=https%3A%2F%2Famzn-science-production-science.s3.us-east-1.amazonaws.com%2Fscience%2Fab%2F95%2F437c6e1d42a9864318f0a9ea4142%2Fsecurity-privacy-and-abuse-prevention-1.png)Security, privacy, and abuse prevention](https://www.amazon.science/research-areas/security-privacy-and-abuse-prevention)
        *   [![Image 26: Reduced padding - Research areas](https://cdn.amazon.science/fc/ba/b7df3c284e6b9afc3487753a1bad/sustainability.svg)Sustainability](https://www.amazon.science/research-areas/sustainability)

    *   
Our scientific contributions
        *   [Publications Research from our scientists and collaborators.](https://www.amazon.science/publications) 
        *   [Conferences Our experts present and discuss cutting-edge research at scientific meetings globally.](https://www.amazon.science/conferences-and-events) 

*   
News & blog  
    *   News & blog
    *   
The latest from Amazon researchers
        *   [Amazon Science Blog Technical deep-dives and perspectives from our scientists.](https://www.amazon.science/blog) 
        *   [News Research milestones and recent achievements.](https://www.amazon.science/news) 

    *   
The latest from Amazon researchers
        *   [Amazon Science Blog Technical deep-dives and perspectives from our scientists.](https://www.amazon.science/blog) 
        *   [News Research milestones and recent achievements.](https://www.amazon.science/news) 

*   
[Collaborations](https://www.amazon.science/academic-engagements/research-collaborations)  
    *   Collaborations
    *   
Amazon Research Awards
        *   [Overview](https://www.amazon.science/research-awards)
        *   [Call for proposals](https://www.amazon.science/research-awards/call-for-proposals)
        *   [Latest news](https://www.amazon.science/research-awards/latest-news)
        *   [Research stories](https://www.amazon.science/research-awards/success-stories)
        *   [Recipients](https://www.amazon.science/research-awards/recipients)

    *   
Amazon Nova AI Challenge
        *   [Overview](https://www.amazon.science/nova-ai-challenge)
        *   [Rules](https://www.amazon.science/nova-ai-challenge/rules)
        *   [FAQs](https://www.amazon.science/nova-ai-challenge/faqs)
        *   [Teams](https://www.amazon.science/nova-ai-challenge/teams/)

    *   
Research collaborations
        *   [Overview](https://www.amazon.science/academic-engagements)
        *   [Carnegie Mellon University](https://www.amazon.science/news/amazon-and-carnegie-mellon-university-launch-strategic-ai-innovation-hub)
        *   [Columbia University](https://www.amazon.science/academic-engagements/columbia-engineering-and-amazon-announce-creation-of-new-york-research-center)
        *   [Hampton University](https://www.amazon.science/academic-engagements/amazon-robotics-hampton-university-team-up-to-establish-robotics-program)
        *   [Howard University](https://www.amazon.science/news-and-features/amazon-and-howard-announce-expansion-of-academic-collaboration)
        *   [IIT Bombay](https://www.amazon.science/news-and-features/amazon-and-iit-bombay-launch-multiyear-collaboration)
        *   [Johns Hopkins University](https://www.amazon.science/academic-engagements/amazon-and-johns-hopkins-announce-new-ai-institute)
        *   [Max Planck Society](https://www.amazon.science/academic-engagements/amazon-and-max-planck-society-launch-science-hub)
        *   [MIT](https://www.amazon.science/academic-engagements/amazon-and-mit-establish-science-hub)
        *   [Tennessee State University](https://www.amazon.science/latest-news/amazon-and-tennessee-state-university-announce-academic-collaboration)
        *   [University of California, Los Angeles](https://www.amazon.science/academic-engagements/amazon-and-ucla-establish-science-hub-for-humanity-and-ai)
        *   [University of Illinois Urbana-Champaign](https://www.amazon.science/news-and-features/amazon-launches-the-aice-center-at-the-university-of-illinois-urbana-champaign)
        *   [University of Southern California](https://www.amazon.science/academic-engagements/usc-and-amazon-establish-center-for-secure-and-trusted-machine-learning)
        *   [University of Texas at Austin](https://www.amazon.science/news-and-features/amazon-and-university-of-texas-at-austin-launch-science-hub)
        *   [Virginia Tech](https://www.amazon.science/academic-engagements/amazon-and-virginia-tech-launch-ai-and-ml-research-initiative)
        *   [University of Washington](https://www.amazon.science/academic-engagements/new-uw-amazon-science-hub-launches)

    *   
Amazon Research Awards
        *   [Overview](https://www.amazon.science/research-awards)
        *   [Call for proposals](https://www.amazon.science/research-awards/call-for-proposals)
        *   [Latest news](https://www.amazon.science/research-awards/latest-news)
        *   [Research stories](https://www.amazon.science/research-awards/success-stories)
        *   [Recipients](https://www.amazon.science/research-awards/recipients)

    *   
Amazon Nova AI Challenge
        *   [Overview](https://www.amazon.science/nova-ai-challenge)
        *   [Rules](https://www.amazon.science/nova-ai-challenge/rules)
        *   [FAQs](https://www.amazon.science/nova-ai-challenge/faqs)
        *   [Teams](https://www.amazon.science/nova-ai-challenge/teams/)

    *   
Research collaborations
        *   [Overview](https://www.amazon.science/academic-engagements)
        *   [Carnegie Mellon University](https://www.amazon.science/news/amazon-and-carnegie-mellon-university-launch-strategic-ai-innovation-hub)
        *   [Columbia University](https://www.amazon.science/academic-engagements/columbia-engineering-and-amazon-announce-creation-of-new-york-research-center)
        *   [Hampton University](https://www.amazon.science/academic-engagements/amazon-robotics-hampton-university-team-up-to-establish-robotics-program)
        *   [Howard University](https://www.amazon.science/news-and-features/amazon-and-howard-announce-expansion-of-academic-collaboration)
        *   [IIT Bombay](https://www.amazon.science/news-and-features/amazon-and-iit-bombay-launch-multiyear-collaboration)
        *   [Johns Hopkins University](https://www.amazon.science/academic-engagements/amazon-and-johns-hopkins-announce-new-ai-institute)
        *   [Max Planck Society](https://www.amazon.science/academic-engagements/amazon-and-max-planck-society-launch-science-hub)
        *   [MIT](https://www.amazon.science/academic-engagements/amazon-and-mit-establish-science-hub)
        *   [Tennessee State University](https://www.amazon.science/latest-news/amazon-and-tennessee-state-university-announce-academic-collaboration)
        *   [University of California, Los Angeles](https://www.amazon.science/academic-engagements/amazon-and-ucla-establish-science-hub-for-humanity-and-ai)
        *   [University of Illinois Urbana-Champaign](https://www.amazon.science/news-and-features/amazon-launches-the-aice-center-at-the-university-of-illinois-urbana-champaign)
        *   [University of Southern California](https://www.amazon.science/academic-engagements/usc-and-amazon-establish-center-for-secure-and-trusted-machine-learning)
        *   [University of Texas at Austin](https://www.amazon.science/news-and-features/amazon-and-university-of-texas-at-austin-launch-science-hub)
        *   [Virginia Tech](https://www.amazon.science/academic-engagements/amazon-and-virginia-tech-launch-ai-and-ml-research-initiative)
        *   [University of Washington](https://www.amazon.science/academic-engagements/new-uw-amazon-science-hub-launches)

*   
Resources  
    *   Resources
    *   
        *   [Code and datasets](https://www.amazon.science/code-and-datasets)
        *   [Amazon Nova Try Amazon’s frontier foundation models.](https://nova.amazon.com/) 

    *   
        *   [Code and datasets](https://www.amazon.science/code-and-datasets)
        *   [Amazon Nova Try Amazon’s frontier foundation models.](https://nova.amazon.com/) 

*   
[Careers](https://www.amazon.science/careers)  
    *   Careers
    *   
        *   [Careers Explore our open roles.](https://www.amazon.science/careers) 
        *   [Amazon Scholars Faculty research opportunities on industry-scale technical challenges.](https://www.amazon.science/scholars) 
        *   [Postdoctoral Science Program Early-career research opportunities alongside experienced industry scientists.](https://www.amazon.science/postdoctoral-science-program) 

    *   
        *   [Careers Explore our open roles.](https://www.amazon.science/careers) 
        *   [Amazon Scholars Faculty research opportunities on industry-scale technical challenges.](https://www.amazon.science/scholars) 
        *   [Postdoctoral Science Program Early-career research opportunities alongside experienced industry scientists.](https://www.amazon.science/postdoctoral-science-program) 

Social

*   [bluesky](https://bsky.app/profile/amazon.science)
*   [threads](https://www.threads.com/@amazonscience)
*   [twitter](https://x.com/AmazonScience)
*   [instagram](https://www.instagram.com/AmazonScience/)
*   [youtube](https://www.youtube.com/c/AmazonScience)
*   [facebook](https://www.facebook.com/AmazonScience)
*   [linkedin](https://www.linkedin.com/showcase/AmazonScience)
*   [github](https://github.com/amazon-science)
*   [rss](https://www.amazon.science/index.rss)

Menu

[![Image 27: Amazon Science](https://cdn.amazon.science/fb/1c/07d25693486eb3d6b49091864af7/amazonscience-squidink.svg)](https://www.amazon.science/)

*   
[Research](https://www.amazon.science/research-areas)  
    *   
Research areas
        *   [![Image 28: Automated reasoning.svg](https://cdn.amazon.science/7c/fb/3a915dcf44b3ae2cac79acf280d8/automated-reasoning.svg)Automated reasoning](https://www.amazon.science/research-areas/automated-reasoning)
        *   [![Image 29: Reduced padding - Research areas](https://cdn.amazon.science/26/0a/47bb5de4438483f43551f13963d9/cloud-and-systems.svg)Cloud and systems](https://www.amazon.science/research-areas/cloud-and-systems)
        *   [![Image 30: Reduced padding - Research areas](https://cdn.amazon.science/6a/16/a6e53bfe46ceab77d292a8cea6af/computer-vision.svg)Computer vision](https://www.amazon.science/research-areas/computer-vision)
        *   [![Image 31: Reduced padding - Research areas](https://cdn.amazon.science/2e/8b/017e23db42f0a6e2c4e12a24f2aa/conversational-ai-and-natural-language-processing.svg)Conversational AI](https://www.amazon.science/research-areas/conversational-ai-natural-language-processing)
        *   [![Image 32: Reduced padding - Research areas](https://cdn.amazon.science/c3/a9/4eaa12b34e018438b648da0984c8/economics.svg)Economics](https://www.amazon.science/research-areas/economics)
        *   [![Image 33: Reduced padding - Research areas](https://cdn.amazon.science/8e/8b/3f08e7fd495c9f3ca8667d280825/information-and-knowledge-management.svg)Information and knowledge management](https://www.amazon.science/research-areas/information-and-knowledge-management)
        *   [![Image 34: Reduced padding - Research areas](https://cdn.amazon.science/9b/85/f1a70d944530ab25b4100eca8ae6/machine-learning.svg)Machine learning](https://www.amazon.science/research-areas/machine-learning)
        *   [![Image 35: Reduced padding - Research areas](https://cdn.amazon.science/af/26/afe9cd8041779f0d098ccd7cc686/operations-research-and-optimization.svg)Operations research and optimization](https://www.amazon.science/research-areas/operations-research-and-optimization)
        *   [![Image 36: Reduced padding - Research areas](https://cdn.amazon.science/30/fa/d9b66fce484290127e3e4319f45e/quantum-technologies.svg)Quantum technologies](https://www.amazon.science/research-areas/quantum-technologies)
        *   [![Image 37: Reduced padding - Research areas](https://cdn.amazon.science/5d/b0/310093db4e0da3496b9bac97b17f/robotics.svg)Robotics](https://www.amazon.science/research-areas/robotics)
        *   [![Image 38: Reduced padding - Research areas](https://cdn.amazon.science/91/f9/abec27f74777b60a69e3e4280228/search-and-information-retrieval.svg)Search and information retrieval](https://www.amazon.science/research-areas/search-and-information-retrieval)
        *   [![Image 39: Security privacy and abuse prevention (1).png](https://cdn.amazon.science/dims4/default/661340e/2147483647/strip/true/crop/180x180+0+0/resize/21x21!/quality/90/?url=https%3A%2F%2Famzn-science-production-science.s3.us-east-1.amazonaws.com%2Fscience%2Fab%2F95%2F437c6e1d42a9864318f0a9ea4142%2Fsecurity-privacy-and-abuse-prevention-1.png)Security, privacy, and abuse prevention](https://www.amazon.science/research-areas/security-privacy-and-abuse-prevention)
        *   [![Image 40: Reduced padding - Research areas](https://cdn.amazon.science/fc/ba/b7df3c284e6b9afc3487753a1bad/sustainability.svg)Sustainability](https://www.amazon.science/research-areas/sustainability)

    *   
Our scientific contributions
        *   [Publications Research from our scientists and collaborators.](https://www.amazon.science/publications) 
        *   [Conferences Our experts present and discuss cutting-edge research at scientific meetings globally.](https://www.amazon.science/conferences-and-events) 

    *   
Research areas
        *   [![Image 41: Automated reasoning.svg](https://cdn.amazon.science/7c/fb/3a915dcf44b3ae2cac79acf280d8/automated-reasoning.svg)Automated reasoning](https://www.amazon.science/research-areas/automated-reasoning)
        *   [![Image 42: Reduced padding - Research areas](https://cdn.amazon.science/26/0a/47bb5de4438483f43551f13963d9/cloud-and-systems.svg)Cloud and systems](https://www.amazon.science/research-areas/cloud-and-systems)
        *   [![Image 43: Reduced padding - Research areas](https://cdn.amazon.science/6a/16/a6e53bfe46ceab77d292a8cea6af/computer-vision.svg)Computer vision](https://www.amazon.science/research-areas/computer-vision)
        *   [![Image 44: Reduced padding - Research areas](https://cdn.amazon.science/2e/8b/017e23db42f0a6e2c4e12a24f2aa/conversational-ai-and-natural-language-processing.svg)Conversational AI](https://www.amazon.science/research-areas/conversational-ai-natural-language-processing)
        *   [![Image 45: Reduced padding - Research areas](https://cdn.amazon.science/c3/a9/4eaa12b34e018438b648da0984c8/economics.svg)Economics](https://www.amazon.science/research-areas/economics)
        *   [![Image 46: Reduced padding - Research areas](https://cdn.amazon.science/8e/8b/3f08e7fd495c9f3ca8667d280825/information-and-knowledge-management.svg)Information and knowledge management](https://www.amazon.science/research-areas/information-and-knowledge-management)
        *   [![Image 47: Reduced padding - Research areas](https://cdn.amazon.science/9b/85/f1a70d944530ab25b4100eca8ae6/machine-learning.svg)Machine learning](https://www.amazon.science/research-areas/machine-learning)
        *   [![Image 48: Reduced padding - Research areas](https://cdn.amazon.science/af/26/afe9cd8041779f0d098ccd7cc686/operations-research-and-optimization.svg)Operations research and optimization](https://www.amazon.science/research-areas/operations-research-and-optimization)
        *   [![Image 49: Reduced padding - Research areas](https://cdn.amazon.science/30/fa/d9b66fce484290127e3e4319f45e/quantum-technologies.svg)Quantum technologies](https://www.amazon.science/research-areas/quantum-technologies)
        *   [![Image 50: Reduced padding - Research areas](https://cdn.amazon.science/5d/b0/310093db4e0da3496b9bac97b17f/robotics.svg)Robotics](https://www.amazon.science/research-areas/robotics)
        *   [![Image 51: Reduced padding - Research areas](https://cdn.amazon.science/91/f9/abec27f74777b60a69e3e4280228/search-and-information-retrieval.svg)Search and information retrieval](https://www.amazon.science/research-areas/search-and-information-retrieval)
        *   [![Image 52: Security privacy and abuse prevention (1).png](https://cdn.amazon.science/dims4/default/661340e/2147483647/strip/true/crop/180x180+0+0/resize/21x21!/quality/90/?url=https%3A%2F%2Famzn-science-production-science.s3.us-east-1.amazonaws.com%2Fscience%2Fab%2F95%2F437c6e1d42a9864318f0a9ea4142%2Fsecurity-privacy-and-abuse-prevention-1.png)Security, privacy, and abuse prevention](https://www.amazon.science/research-areas/security-privacy-and-abuse-prevention)
        *   [![Image 53: Reduced padding - Research areas](https://cdn.amazon.science/fc/ba/b7df3c284e6b9afc3487753a1bad/sustainability.svg)Sustainability](https://www.amazon.science/research-areas/sustainability)

    *   
Our scientific contributions
        *   [Publications Research from our scientists and collaborators.](https://www.amazon.science/publications) 
        *   [Conferences Our experts present and discuss cutting-edge research at scientific meetings globally.](https://www.amazon.science/conferences-and-events) 

*   
News & blog  
    *   
The latest from Amazon researchers
        *   [Amazon Science Blog Technical deep-dives and perspectives from our scientists.](https://www.amazon.science/blog) 
        *   [News Research milestones and recent achievements.](https://www.amazon.science/news) 

    *   
The latest from Amazon researchers
        *   [Amazon Science Blog Technical deep-dives and perspectives from our scientists.](https://www.amazon.science/blog) 
        *   [News Research milestones and recent achievements.](https://www.amazon.science/news) 

*   
[Collaborations](https://www.amazon.science/academic-engagements/research-collaborations)  
    *   
Amazon Research Awards
        *   [Overview](https://www.amazon.science/research-awards)
        *   [Call for proposals](https://www.amazon.science/research-awards/call-for-proposals)
        *   [Latest news](https://www.amazon.science/research-awards/latest-news)
        *   [Research stories](https://www.amazon.science/research-awards/success-stories)
        *   [Recipients](https://www.amazon.science/research-awards/recipients)

    *   
Amazon Nova AI Challenge
        *   [Overview](https://www.amazon.science/nova-ai-challenge)
        *   [Rules](https://www.amazon.science/nova-ai-challenge/rules)
        *   [FAQs](https://www.amazon.science/nova-ai-challenge/faqs)
        *   [Teams](https://www.amazon.science/nova-ai-challenge/teams/)

    *   
Research collaborations
        *   [Overview](https://www.amazon.science/academic-engagements)
        *   [Carnegie Mellon University](https://www.amazon.science/news/amazon-and-carnegie-mellon-university-launch-strategic-ai-innovation-hub)
        *   [Columbia University](https://www.amazon.science/academic-engagements/columbia-engineering-and-amazon-announce-creation-of-new-york-research-center)
        *   [Hampton University](https://www.amazon.science/academic-engagements/amazon-robotics-hampton-university-team-up-to-establish-robotics-program)
        *   [Howard University](https://www.amazon.science/news-and-features/amazon-and-howard-announce-expansion-of-academic-collaboration)
        *   [IIT Bombay](https://www.amazon.science/news-and-features/amazon-and-iit-bombay-launch-multiyear-collaboration)
        *   [Johns Hopkins University](https://www.amazon.science/academic-engagements/amazon-and-johns-hopkins-announce-new-ai-institute)
        *   [Max Planck Society](https://www.amazon.science/academic-engagements/amazon-and-max-planck-society-launch-science-hub)
        *   [MIT](https://www.amazon.science/academic-engagements/amazon-and-mit-establish-science-hub)
        *   [Tennessee State University](https://www.amazon.science/latest-news/amazon-and-tennessee-state-university-announce-academic-collaboration)
        *   [University of California, Los Angeles](https://www.amazon.science/academic-engagements/amazon-and-ucla-establish-science-hub-for-humanity-and-ai)
        *   [University of Illinois Urbana-Champaign](https://www.amazon.science/news-and-features/amazon-launches-the-aice-center-at-the-university-of-illinois-urbana-champaign)
        *   [University of Southern California](https://www.amazon.science/academic-engagements/usc-and-amazon-establish-center-for-secure-and-trusted-machine-learning)
        *   [University of Texas at Austin](https://www.amazon.science/news-and-features/amazon-and-university-of-texas-at-austin-launch-science-hub)
        *   [Virginia Tech](https://www.amazon.science/academic-engagements/amazon-and-virginia-tech-launch-ai-and-ml-research-initiative)
        *   [University of Washington](https://www.amazon.science/academic-engagements/new-uw-amazon-science-hub-launches)

    *   
Amazon Research Awards
        *   [Overview](https://www.amazon.science/research-awards)
        *   [Call for proposals](https://www.amazon.science/research-awards/call-for-proposals)
        *   [Latest news](https://www.amazon.science/research-awards/latest-news)
        *   [Research stories](https://www.amazon.science/research-awards/success-stories)
        *   [Recipients](https://www.amazon.science/research-awards/recipients)

    *   
Amazon Nova AI Challenge
        *   [Overview](https://www.amazon.science/nova-ai-challenge)
        *   [Rules](https://www.amazon.science/nova-ai-challenge/rules)
        *   [FAQs](https://www.amazon.science/nova-ai-challenge/faqs)
        *   [Teams](https://www.amazon.science/nova-ai-challenge/teams/)

    *   
Research collaborations
        *   [Overview](https://www.amazon.science/academic-engagements)
        *   [Carnegie Mellon University](https://www.amazon.science/news/amazon-and-carnegie-mellon-university-launch-strategic-ai-innovation-hub)
        *   [Columbia University](https://www.amazon.science/academic-engagements/columbia-engineering-and-amazon-announce-creation-of-new-york-research-center)
        *   [Hampton University](https://www.amazon.science/academic-engagements/amazon-robotics-hampton-university-team-up-to-establish-robotics-program)
        *   [Howard University](https://www.amazon.science/news-and-features/amazon-and-howard-announce-expansion-of-academic-collaboration)
        *   [IIT Bombay](https://www.amazon.science/news-and-features/amazon-and-iit-bombay-launch-multiyear-collaboration)
        *   [Johns Hopkins University](https://www.amazon.science/academic-engagements/amazon-and-johns-hopkins-announce-new-ai-institute)
        *   [Max Planck Society](https://www.amazon.science/academic-engagements/amazon-and-max-planck-society-launch-science-hub)
        *   [MIT](https://www.amazon.science/academic-engagements/amazon-and-mit-establish-science-hub)
        *   [Tennessee State University](https://www.amazon.science/latest-news/amazon-and-tennessee-state-university-announce-academic-collaboration)
        *   [University of California, Los Angeles](https://www.amazon.science/academic-engagements/amazon-and-ucla-establish-science-hub-for-humanity-and-ai)
        *   [University of Illinois Urbana-Champaign](https://www.amazon.science/news-and-features/amazon-launches-the-aice-center-at-the-university-of-illinois-urbana-champaign)
        *   [University of Southern California](https://www.amazon.science/academic-engagements/usc-and-amazon-establish-center-for-secure-and-trusted-machine-learning)
        *   [University of Texas at Austin](https://www.amazon.science/news-and-features/amazon-and-university-of-texas-at-austin-launch-science-hub)
        *   [Virginia Tech](https://www.amazon.science/academic-engagements/amazon-and-virginia-tech-launch-ai-and-ml-research-initiative)
        *   [University of Washington](https://www.amazon.science/academic-engagements/new-uw-amazon-science-hub-launches)

*   
Resources  
    *   
        *   [Code and datasets](https://www.amazon.science/code-and-datasets)
        *   [Amazon Nova Try Amazon’s frontier foundation models.](https://nova.amazon.com/) 

    *   
        *   [Code and datasets](https://www.amazon.science/code-and-datasets)
        *   [Amazon Nova Try Amazon’s frontier foundation models.](https://nova.amazon.com/) 

*   
[Careers](https://www.amazon.science/careers)  
    *   
        *   [Careers Explore our open roles.](https://www.amazon.science/careers) 
        *   [Amazon Scholars Faculty research opportunities on industry-scale technical challenges.](https://www.amazon.science/scholars) 
        *   [Postdoctoral Science Program Early-career research opportunities alongside experienced industry scientists.](https://www.amazon.science/postdoctoral-science-program) 

    *   
        *   [Careers Explore our open roles.](https://www.amazon.science/careers) 
        *   [Amazon Scholars Faculty research opportunities on industry-scale technical challenges.](https://www.amazon.science/scholars) 
        *   [Postdoctoral Science Program Early-career research opportunities alongside experienced industry scientists.](https://www.amazon.science/postdoctoral-science-program) 

Search Submit Search

![Image 54: CompressionModels-03-16x9.png](https://cdn.amazon.science/dims4/default/1d3b996/2147483647/strip/true/crop/1920x1080+0+0/resize/1440x810!/quality/90/?url=https%3A%2F%2Famzn-science-production-science.s3.us-east-1.amazonaws.com%2Fscience%2F28%2F46%2F0121ba1e4b42be0c56e7560c9844%2Fcompressionmodels-03-16x9.png)

The more your listener already knows, the shorter the message you need to send. An expert ML engineer needs only a few sentences; a newcomer needs the whole manual.

[Machine learning](https://www.amazon.science/research-areas/machine-learning)

# Why don’t machine learning research agents overfit?

## New research indicates that AI agents learn compressible models of data, which don’t have enough space to enable memorization.

By[Martin Bertran Lopez](https://www.amazon.science/author/martin-bertran-lopez),[Aaron Roth](https://www.amazon.science/author/aaron-roth)

 September 10, 2026 

11 min read

[Share](https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit)

Share

*   [Copy link](https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit)
*   [Email](mailto:?body=Why%20don%E2%80%99t%20machine%20learning%20research%20agents%20overfit%3F%0A%0Ahttps%3A%2F%2Fwww.amazon.science%2Fblog%2Fwhy-dont-machine-learning-research-agents-overfit%0A%0ANew%20research%20indicates%20that%20AI%20agents%20learn%20compressible%20models%20of%20data%2C%20which%20don%E2%80%99t%20have%20enough%20space%20to%20enable%20memorization.)
*   [X](https://twitter.com/intent/tweet?url=https%3A%2F%2Fwww.amazon.science%2Fblog%2Fwhy-dont-machine-learning-research-agents-overfit&text=Why%20don%E2%80%99t%20machine%20learning%20research%20agents%20overfit%3F)
*   [LinkedIn](https://www.linkedin.com/shareArticle?url=https%3A%2F%2Fwww.amazon.science%2Fblog%2Fwhy-dont-machine-learning-research-agents-overfit&mini=true&title=Why%20don%E2%80%99t%20machine%20learning%20research%20agents%20overfit%3F&summary=New%20research%20indicates%20that%20AI%20agents%20learn%20compressible%20models%20of%20data%2C%20which%20don%E2%80%99t%20have%20enough%20space%20to%20enable%20memorization.&source=Amazon%20Science)
*   [Facebook](https://www.facebook.com/dialog/share?app_id=1024652704536162&display=popup&href=https%3A%2F%2Fwww.amazon.science%2Fblog%2Fwhy-dont-machine-learning-research-agents-overfit)
*   [Line](https://social-plugins.line.me/lineit/share?url=https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit)
*   [Reddit](https://www.reddit.com/submit?url=https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit&title=Why%20don%E2%80%99t%20machine%20learning%20research%20agents%20overfit?)
*   [QZone](http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url=https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit&title=Why%20don%E2%80%99t%20machine%20learning%20research%20agents%20overfit?&summary=New%20research%20indicates%20that%20AI%20agents%20learn%20compressible%20models%20of%20data,%20which%20don%E2%80%99t%20have%20enough%20space%20to%20enable%20memorization.)
*   [Sina Weibo](https://service.weibo.com/share/share.php?url=https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit)
*   [WeChat](https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit "Share on wechat")
*   [WhatsApp](https://api.whatsapp.com/send?text=Why%20don%E2%80%99t%20machine%20learning%20research%20agents%20overfit?%20https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit)

 分享到微信 

x

 Key takeaways 

*   ML models don't overfit benchmarks, even after many rounds of iterative improvement. This contradicts textbook predictions that repeatedly evaluating against the same held-out data should lead to overfitting.
*   Experiments with ML research agents indicate that successful strategies are highly compressible. When a successful agent's strategy is squeezed through an information bottleneck (as few as 16 tokens), a fresh agent with no memory can reproduce the original agent's performance, meaning the strategy captured real structure, not memorized data.
*   Compression provides both an explanation and a diagnostic tool. Strategies that genuinely overfit fail the compression test: their validation-specific gains vanish when passed through the bottleneck.
*   LLMs are powerful compression decoders. Because they carry vast world knowledge, they can reconstruct full ML pipelines from terse, expert-shorthand prompts, which is a concrete way of understanding why they're so capable.

Was this answer helpful?

Machine learning, at its core, is about generalization, not memorization. You hand your learning algorithm a pile of training examples and use them to fit a model. But the goal is not to perform well on the training examples — that's easy, you could just memorize the answers. The goal is to perform well on _new_ examples that you have never before seen. If a model does well on the data it was trained on but poorly on fresh data, it hasn’t actually learned anything; you have only fooled yourself into thinking it has. This failure mode has a name: overfitting.

Anyone who has taken an introductory statistics or machine learning class knows the standard defense. You hold out some of your data and refuse to train on it. In practice, this held-out data plays two roles. A _validation set_ is one you consult repeatedly while building the model — to compare candidates, tune hyperparameters, and decide what to try next. A final _test set_ (or _holdout_) is meant to be touched only once, at the very end: because the training procedure never saw it, strong performance there is a correct proxy for the new examples you will encounter in the wild.

> Machine learning, at its core, is about generalization, not memorization

The “holdout” condition is crucial, though. The correct-proxy guarantee holds if the held-out set stays genuinely unseen. If you check your performance on it, tweak your training procedure in response, recheck, and iterate, chasing better and better numbers, that set is no longer unseen; it has become part of your training procedure. Do this enough times, and you can overfit it just as you might have overfit the training set, and you have lost your proxy for unseen data. This is true of any held-out set you reuse this way, including a validation set, which is reused by design.

## A puzzle at the heart of machine learning

Real machine learning research looks _exactly_ like the iterative improvement loop we just described. Everyone gauges performance using a handful of benchmark datasets that go unrevised for years. The research community repeats an enormous, distributed loop: evaluate a model on the benchmark, revise the training procedure, re-evaluate, publish, and let the next group eke out a little more improvement.

This is precisely the kind of hill-climbing against a held-out set that, by the textbook account, ought to produce rampant overfitting. By now, the leaderboards should be saturated with models that look great on the benchmark and mediocre everywhere else.

And yet that is not what happens. Studies that build entirely fresh test sets for old, heavily reused benchmarks have found that improvements largely _transfer_: on the new data, models demonstrate the same gains they did on the old benchmark. Benchmark-driven machine learning, against the textbook's prediction, has produced rapid and largely _real_ progress. Why?

There is no shortage of hypotheses, but they have been hard to test empirically, because the "subject" of the experiment is the entire human research community. You cannot reset a field, wipe its memory, and rerun the last decade under controlled conditions.

But we can do something similar. We now have capable, LLM-based research agents that can autonomously run the same machine-learning optimization loops that human communities run. They engage in the same benchmark hill-climbing — and, intriguingly, they too seem not to overfit. The difference is that an agent, unlike a research community, is something you _can_ reset. You can clear its memory, control exactly what information it sees, and run the experiment again. In a recent paper, "[What fits (into few tokens) doesn't overfit: Compression and generalization in ML research agents](https://arxiv.org/abs/2606.11045)", we do exactly that — and in the process offer a concrete explanation for the long-standing mystery.

## Occam's razor, made precise

The explanation begins with a very old idea. Occam's razor says that among hypotheses that explain the data equally well, the simpler one is more likely to be correct. It turns out this intuition has a precise mathematical form, and it is what underlies the whole story.

Suppose you can describe your hypothesis — your model, your strategy — in a small number of bits, far fewer than it would take to memorize the training data. If that compact hypothesis performs very well on the training data, it must also perform well on new data.

<!-- media:video-gif src="https://cdn.amazon.science/72/eb/d021ebfc445d8f4acd2fe2ac211c/compressionmodels-01-1x1.mp4" -->

[Video 5](https://cdn.amazon.science/72/eb/d021ebfc445d8f4acd2fe2ac211c/compressionmodels-01-1x1.mp4)

Video Player is loading.

Play Video

Play

Mute

Current Time 0:00

/

Duration 0:00

Loaded: 0%

Stream Type LIVE

Seek to live, currently behind live LIVE

Remaining Time-0:00

1x

Playback Rate

Chapters

*   Chapters

Descriptions

*   descriptions off, selected

Captions

*   captions and subtitles off, selected

Audio Track

Picture-in-Picture Fullscreen

This is a modal window.

Beginning of dialog window. Escape will cancel and close the window.

Text Color Transparency Background Color Transparency Window Color Transparency 

Font Size Text Edge Style Font Family

Reset restore all settings to the default values Done

Close Modal Dialog
End of dialog window.

Occam's razor, formalized: among hypotheses that explain the data equally well, the simpler one — describable in fewer bits — is more likely to generalize to new examples.

The reasoning runs through a counting argument. There simply are not very many _short_ descriptions, because there are not very many short strings. The fewer candidate hypotheses there are, the less likely it is that any one of them fooled you on the training set by luck — even though you used the training set to guide your search.

Another way to get the intuition: if your compressed description is too small to secretly record the training data, then when it performs well on the training data, it cannot be because it memorized the answers — it didn't have space to do that. It must be because it captured something true about the data's structure. Short descriptions cannot cheat because there isn't room.

Here is an attractive hypothesis: _successful machine learning strategies are highly compressible._ A researcher might stare at thousands of benchmark scores over the course of a project, but the strategy that ultimately survives is usually a short list of familiar choices — an architecture family, an optimizer, a learning-rate schedule, a data-handling recipe, a regularization scheme. If that final recipe can be communicated in just a few bits, then the model's true dependence on the benchmark is far smaller than the long, winding transcript of experiments would suggest. The hill-climbing was extensive, but the thing that came out the other end was — or could have been — tiny.

## Compression, intelligence, and the power of a knowledgeable listener

Imagine trying to explain a specific machine learning pipeline to a bright high-school student, in enough detail that they could actually reproduce it. It would be a long, laborious conversation. You would have to explain what gradient descent is, what a neural network is, what PyTorch or JAX or TensorFlow does, what a learning rate is, and on and on. Almost none of that is specific to _your_ problem; it is general background about how machine learning works.

Now imagine explaining the same pipeline to an expert ML engineer. The conversation now collapses to a few sentences. You skip everything that counts as common knowledge and communicate only what is genuinely specific to _this_ problem: the architecture choice, the batch size, the optimizer, a couple of hyperparameters. The more your listener already knows about the world, the shorter the message you need to send — and the more aggressively you can compress. None of this "world knowledge" counts against you in the Occam's-razor argument, because you could have written all of that down without having looked at the training set.

This is where large language models enter the picture. Modern LLMs carry an enormous amount of world knowledge. They know how ML tooling works; they know the standard optimization algorithms; they know the conventional hyperparameter choices and the common defaults. If a detail is left unspecified, they can fill in a plausible value. That makes them extraordinarily good _compression decoders_: hand an LLM a terse, expert-to-expert message, and it can unpack it into a full, working procedure. If you think about it, this is exactly why they are so powerful.

## The experiment: Squeezing a strategy through a bottleneck

This suggests a clean experiment. Have an ML research agent — _the explorer_ — try to solve a new machine learning problem. Give it full access to a validation set and let it experiment and iterate freely, chasing better validation performance over hundreds of rounds. Here the validation set plays the role of the benchmark: a _reusable holdout_ the agent queries again and again. This is the hill-climbing loop that _ought_ to overfit.

Then test how compressible the solution is. A second agent, the _compressor_, reads the entire transcript of the explorer's work and tries to distill the winning strategy into a very short prompt — just a handful of tokens. That prompt is handed to a third agent, the _reproducer_, which must implement the strategy from scratch using only the prompt and the training data. Critically, the reproducer has _no_ access to the validation set, the explorer's code, or its transcript. The short prompt is the only channel through which anything learned from the validation set can reach it. (In the study we report in our paper, the compressor and reproducer are both Claude models.)

If the reproducer — starting cold, armed only with a few tokens — matches the explorer's performance, then all the validation-dependent information needed to specify the strategy fit through that tiny channel. The strategy was compressible. We call this a certificate of _output compression_.

The setup has a very useful property that human research communities lack: the reproducer can be reset over and over. The compressor can try many different compressions and see how well each is decoded, because every attempt lands on a fresh reproducer with no memory of the last one. It is a little like the film _Memento_ — you are leaving a terse note for a version of yourself whose memory will be wiped before reading it. You learn to write notes that a knowledgeable but amnesiac copy of you can act on; those notes can be very short because the receiver will fill in anything you leave unsaid exactly as you would have.

![Image 55: CompressionModels-04-1x1.png](https://cdn.amazon.science/dims4/default/3359a84/2147483647/strip/true/crop/1920x1080+0+0/resize/1200x675!/quality/90/?url=https%3A%2F%2Famzn-science-production-science.s3.us-east-1.amazonaws.com%2Fscience%2Fac%2Fbd%2Fb0c9558b4052a883f75e6d2f47f3%2Fcompressionmodels-04-1x1.png)

In the researchers' experiments, an explorer agent's strategy is squeezed through a narrow information bottleneck. Whatever survives compression must reflect real structure, not memorized data.

## What comes out the other end

The compressions turn out to be remarkably small. Across eight datasets — spanning tabular classification, image classification, language modeling, diffusion modeling, and reward modeling — 32-token prompts were enough for a fresh reproducer to match the explorer's adaptively optimized models on the large majority of problems. One language-modeling strategy survived compression down to just 16 tokens with no loss in held-out performance.

What do these prompts actually look like? The most revealing examples are right at the border of conciseness where the compression almost breaks. In one language-modeling experiment, the explorer discovered a custom GPT-style training recipe. Under a 16-token budget, this was still enough for fresh reproducers to match the uncompressed explorer:

**QKn 12L768 Mu .1 R² b2M 4x**

To a human reader this looks cryptic, but to another ML agent it says something concrete: _QKn_ means “QK normalization”, _12L768_ means a 12-layer, 768-dimensional transformer, _Mu .1_ means the Muon optimizer with learning rate 0.1, _R²_ means squared-ReLU activations, _b2M_ means a two-million-token batch, and _4x_ means a fourfold feed-forward block. Cut the budget to eight tokens, however, and the prompt becomes

**12L768 Mu .1 R²**

Now the reproducer no longer matches the explorer. The missing pieces specified real training choices that were made as a function of the data and differ from the most obvious defaults. This boundary shows the limits of compressibility and is important. It shows that the reproducer is not succeeding from prior knowledge alone. A few compressed tokens are carrying genuine information learned from the data itself, and when those tokens disappear, so does the performance.

We also ran a set of experiments that imposed an information bottleneck from the other direction. Instead of compressing the explorer's _output_, we compressed its _input_: rather than telling the explorer each model's numerical validation score, we returned only a single bit — did this model beat the running best, or not? Even reduced to one bit of feedback per query, the explorer found strategies as good as those it found with full numerical scores. The channel between the validation set and the final strategy is narrow in both directions, and the one-bit version even comes with a rigorous mathematical guarantee on generalization.

<!-- media:video-gif src="https://cdn.amazon.science/18/ff/a70ce9fd4f878910640f3d0afeaa/compressionmodels-02-16x9.mp4" -->

[Video 6](https://cdn.amazon.science/18/ff/a70ce9fd4f878910640f3d0afeaa/compressionmodels-02-16x9.mp4)

Video Player is loading.

Play Video

Play

Mute

Current Time 0:00

/

Duration 0:00

Loaded: 0%

Stream Type LIVE

Seek to live, currently behind live LIVE

Remaining Time-0:00

1x

Playback Rate

Chapters

*   Chapters

Descriptions

*   descriptions off, selected

Captions

*   captions and subtitles off, selected

Audio Track

Picture-in-Picture Fullscreen

This is a modal window.

Beginning of dialog window. Escape will cancel and close the window.

Text Color Transparency Background Color Transparency Window Color Transparency 

Font Size Text Edge Style Font Family

Reset restore all settings to the default values Done

Close Modal Dialog
End of dialog window.

Across eight datasets, strategies that emerged from hundreds of iterative experiments could be compressed into prompts as short as 16 to 32 tokens — small enough for a fresh agent with no memory to reproduce the original results.

## Catching cheaters

A good empirical theory should be falsifiable — and this one is. If low overfitting is really explained by compressibility, then models that _genuinely_ overfit should fail to be compressible via this pipeline.

To check, we deliberately pushed agents into overfitting by handing them direct validation-set access and prompting them to maximize validation performance at any cost. The agents took the bait: in 38 of 102 experimental runs, validation accuracy ran more than 10% ahead of true held-out accuracy.

The theory predicts that these gains should not survive the compression bottleneck, because they encode idiosyncrasies of specific validation examples, not transferable structure. Sure enough, when squeezed through a short prompt to a fresh reproducer, the validation-specific advantages vanished. Compression separated the legitimate strategies from the overfitting ones with very high accuracy.

So compression does not merely _explain_ why autonomous research agents tend not to overfit but offers a tool for _catching_ overfitting when it does occur, by flagging the cases where no short description can reproduce the result.

## What this tells us — and what it doesn't

A few caveats are in order. The whole framework assumes that the only path from the validation data to the final model runs through the prompt we feed the reproducer. Of course, if a model had memorized the validation data during pretraining, it would have a side channel that bypasses the information bottleneck we are trying to impose. We don't think that is what is happening in our experiments: agents improve gradually through real search rather than starting at their best, and performance degrades at very short token budgets. But fully resolving this question will likely require experimenting with fresh datasets collected after a model's training cutoff, which we haven’t done.

Most importantly, our results are about LLM agents, because that is where the experiment is possible — where you can reset the subject, control its inputs, and count their length. But the picture they paint is strongly suggestive about human research communities too. When a field spends years climbing a fixed benchmark, and the gains keep transferring to fresh data, it may be for the same reason the agents' strategies survive a 32-token prompt: the recipes that actually work are simple. Or in other words, "What fits (into few tokens) doesn't overfit."

**Acknowledgments:** Steven Wu

 Research areas 

*   [Machine learning](https://www.amazon.science/research-areas/machine-learning)

 Tags 

*   [Generative AI](https://www.amazon.science/tag/generative-models)
*   [Agentic AI](https://www.amazon.science/tag/agentic-ai)
*   [Language models](https://www.amazon.science/tag/language-models)

About the Author

[Martin Bertran Lopez](https://www.amazon.science/author/martin-bertran-lopez)

 Martin Bertran Lopez is an applied scientist in Amazon Web Services' Privacy organization. 

[Aaron Roth](https://www.amazon.science/author/aaron-roth)

 Aaron Roth is the Henry Salvatori Professor of Computer and Cognitive Science at the University of Pennsylvania and an Amazon Scholar. His research focuses on the algorithmic foundations of data privacy, algorithmic fairness, game theory, learning theory, and machine learning. Together with Cynthia Dwork, he is the author of the book [_The Algorithmic Foundations of Differential Privacy_](https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf); together with [Michael Kearns](https://www.amazon.science/author/michael-kearns), he is the author of [_The Ethical Algorithm: The Science of Socially Aware Algorithm Design_](https://www.amazon.com/Ethical-Algorithm-Science-Socially-Design-ebook/dp/B07XLTXBXV). 

[](https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit)

## Related content

*   [![Image 56: PortableReasoning-Hero-16x9.png](https://cdn.amazon.science/dims4/default/be98661/2147483647/strip/true/crop/1920x1076+0+2/resize/1240x695!/quality/90/?url=https%3A%2F%2Famzn-science-production-science.s3.us-east-1.amazonaws.com%2Fscience%2Fae%2F23%2F55a2d7b84eb0bfdebe5445bc7e35%2Fportablereasoning-hero-16x9.png)](https://www.amazon.science/blog/portable-reasoning-releasing-text-bound-intelligence-into-agentic-interaction) [Portable reasoning: Releasing text-bound intelligence into agentic interaction](https://www.amazon.science/blog/portable-reasoning-releasing-text-bound-intelligence-into-agentic-interaction) Meiqi Sun April 20, 2026  Large language models today can solve algebra, pass academic benchmarks, and generate highly structured chain-of-thought explanations. In text-only settings, they often feel startlingly intelligent — methodical, articulate, even strategic. But place those models inside an interactive environment — ask them to click buttons, scroll pages, fill out forms, and submit answers — and their behavior changes. Their careful reasoning falters. They guess where they once deduced. They adhere to templates and produce limited procedural narration: stating what they see and what they will click next, without first forming a structured plan and acting in accordance with plan. It’s as if part of their intelligence has quietly gone offline the moment the cursor appears. Machine learning   
*   [![Image 57: Promptimus-02b-16x9.png](https://cdn.amazon.science/dims4/default/b06de92/2147483647/strip/true/crop/1920x1076+0+2/resize/1240x695!/quality/90/?url=https%3A%2F%2Famzn-science-production-science.s3.us-east-1.amazonaws.com%2Fscience%2F71%2F43%2Fed92ff934c64892903a6cc1c9f39%2Fpromptimus-02b-16x9.png)](https://www.amazon.science/blog/promptimus-improving-already-good-llm-prompts-with-zero-manual-engineering) [Promptimus: Improving already good LLM prompts with zero manual engineering](https://www.amazon.science/blog/promptimus-improving-already-good-llm-prompts-with-zero-manual-engineering) [Zhengyuan Shen](https://www.amazon.science/author/zhengyuan-shen), [Yunfei Bai](https://www.amazon.science/author/yunfei-bai), [Sullam Jeoung](https://www.amazon.science/author/sullam-jeoung), [Shuai Wang](https://www.amazon.science/author/shuai-wang) May 14, 2026  By focusing on specific failure points and suggesting targeted solutions, a new automated prompt-engineering framework improves prompt performance without compromising existing functionality.   
*   [![Image 58: MolecularProperties-02-16x9.gif](https://cdn.amazon.science/dims4/default/d720f56/2147483647/strip/true/crop/1920x1076+0+2/resize/1240x695!/quality/90/?url=https%3A%2F%2Famzn-science-production-science.s3.us-east-1.amazonaws.com%2Fscience%2F6b%2Fbc%2F16f0ccb54763af207e07be541a44%2Fmolecularproperties-02-16x9.gif)](https://www.amazon.science/blog/customized-amazon-nova-models-improve-molecular-property-prediction-in-drug-discovery) [Customized Amazon Nova models improve molecular-property prediction in drug discovery](https://www.amazon.science/blog/customized-amazon-nova-models-improve-molecular-property-prediction-in-drug-discovery) [Krishnateja Killamsetty](https://www.amazon.science/author/krishnateja-killamsetty), [Andy Lapastora](https://www.amazon.science/author/andy-lapastora), Karthick Prasad Gunasekaran April 15, 2026  A single, optimized LLM unifies what previously required multiple models and can serve as a reasoning partner for medical chemists. [Machine learning](https://www.amazon.science/research-areas/machine-learning)   

[](https://www.amazon.science/blog/why-dont-machine-learning-research-agents-overfit)

## Work with us

[See more jobs](https://www.amazon.science/careers)[See more jobs](https://www.amazon.science/careers)

[Data Scientist II, Last Mile Science](https://www.amazon.jobs/jobs/10544231/data-scientist-ii-last-mile-science?cmpid=bsp-amazon-science)

IN, KA, Bangalore

Does the thought of improving one of the world’s most complex logistic systems inspire you? Is your passion to sift through hundreds of systems, processes, and data sources to solve the puzzle and identify the next big opportunity? Are you a creative big thinker who is passionate about using data to direct decision making and solve complex and large-scale challenges? Are you fascinated by the interactions between operations and strategy? Do you feel like your skills uniquely qualify you to bridge communication between teams with competing priorities? If so, then this position is for you! Come help Amazon create state-of-the-art science-driven technologies for delivering packages to the doorstep of our customers! The Last Mile Routing & Planning organization builds the software, algorithms and tools that make the “magic” of home delivery happen: our flow, sort, dispatch and routing intelligence systems are responsible for the billions of daily decisions needed to plan and execute safe, efficient and frustration-free routes for drivers around the world. Our team supports deliveries (and pickups!) for Amazon Logistics, Same Day, Amazon Grocery, Lockers, and other new initiatives across the world. Key job responsibilities In this role, your main focus will be to apply algorithms, synthesize information, identify business opportunities, provide data-driven insights and communicate business and technical requirements within the team and across stakeholder groups. You will partner closely with other scientists and engineers in a collegial environment with a clear path to business impact. We have an exciting portfolio of research areas including vehicle routing, planning for electric and autonomous vehicles, district and stops planning, ultra-fast deliveries, fleet planning, and forecasting solutions for different delivery programs leveraging the latest OR, ML, and Generative AI methods, at a global scale. Successful candidates will have a deep knowledge of Operations Research and/or Machine/Deep Learning methods, experience in applying these methods to large-scale business problems, the ability to map models into production-worthy code in Python or Java, the communication skills necessary to explain complex technical approaches to a variety of stakeholders and customers, and the excitement to take iterative approaches to tackle big research challenges.

[Applied Scientist, Fauna](https://www.amazon.jobs/jobs/10543848/applied-scientist-fauna?cmpid=bsp-amazon-science)

US, NY, New York

We are seeking an Applied Scientist to lead the development of evaluation frameworks and data collection protocols for robotic capabilities. In this role, you will focus on designing how we measure, stress-test, and improve robot behavior across a wide range of real-world tasks. Your work will play a critical role in shaping how policies are validated and how high-quality datasets are generated to accelerate system performance. You will operate at the intersection of robotics, machine learning, and human-in-the-loop systems, building the infrastructure and methodologies that connect teleoperation, evaluation, and learning. This includes developing evaluation policies, defining task structures, and contributing to operator-facing interfaces that enable scalable and reliable data collection. The ideal candidate is highly experimental, systems-oriented, and comfortable working across software, robotics, and data pipelines, with a strong focus on turning ambiguous capability goals into measurable and actionable evaluation systems. Key job responsibilities - Design and implement evaluation frameworks to measure robot capabilities across structured tasks, edge cases, and real-world scenarios - Develop task definitions, success criteria, and benchmarking methodologies that enable consistent and reproducible evaluation of policies - Create and refine data collection protocols that generate high-quality, task-relevant datasets aligned with model development needs - Build and iterate on teleoperation workflows and operator interfaces to support efficient, reliable, and scalable data collection - Analyze evaluation results and collected data to identify performance gaps, failure modes, and opportunities for targeted data collection - Collaborate with engineering teams to integrate evaluation tooling, logging systems, and data pipelines into the broader robotics stack - Stay current with advances in robotics, evaluation methodologies, and human-in-the-loop learning to continuously improve internal approaches - Lead technical projects from conception through production deployment - Mentor junior scientists and engineers About the team Fauna Robotics, an Amazon company, is building capable, safe, and genuinely delightful robots for everyday life. Our goal is simple: make robots people actually want to live and interact with in everyday human spaces. We believe that future won’t arrive until building for robotics becomes far more accessible. Today, too much effort is spent reinventing the fundamentals. We’re changing that by developing tightly integrated hardware and software systems that make it faster, safer, and more intuitive to create real-world robotic products. Our work spans the full stack: mechanical design, control systems, dynamic modeling, and intelligent software. The focus is not just functionality, but experience. We’re building robots that feel responsive, expressive, and genuinely useful. At Fauna, you’ll work at the frontier of this space, helping define how robots move, manipulate, and interact with people in natural environments. It’s an opportunity to solve hard problems across hardware and software with a team focused on making robotics accessible and joyful to build. If you care about making robotics real for everyone and building systems that are as delightful as they are capable, we’re interested in hearing from you.

[Applied Scientist II, Foundation Model](https://www.amazon.jobs/jobs/10543793/applied-scientist-ii-foundation-model?cmpid=bsp-amazon-science)

US, CA, Sunnyvale

Industrial is seeking exceptional talent to help develop the next generation of advanced robotics systems that will transform automation at Amazon's scale. We're building revolutionary robotic systems that combine innovative AI, sophisticated control systems, and advanced mechanical design to create adaptable automation solutions capable of working safely alongside humans in dynamic environments. This is a unique opportunity to shape the future of robotics and automation at unprecedented scale, working with world-class teams pushing the boundaries of what's possible in robotic manipulation, locomotion, and human-robot interaction. This role presents an opportunity to shape the future of robotics through innovative applications of deep learning and large language models. We leverage advanced robotics, machine learning, and artificial intelligence to solve complex operational challenges at unprecedented scale. Our fleet of robots operates across hundreds of facilities worldwide, working in sophisticated coordination to fulfill our mission of customer excellence. We are pioneering the development of robotics foundation models that: - Enable unprecedented generalization across diverse tasks - Integrate multi-modal learning capabilities (visual, tactile, linguistic) - Accelerate skill acquisition through demonstration learning - Enhance robotic perception and environmental understanding - Streamline development processes through reusable capabilities The ideal candidate will contribute to research that bridges the gap between theoretical advancement and practical implementation in robotics. You will be part of a team that's revolutionizing how robots learn, adapt, and interact with their environment. Join us in building the next generation of intelligent robotics systems that will transform the future of automation and human-robot collaboration. As an Applied Scientist, you will develop and improve machine learning systems that help robots perceive, reason, and act in real-world environments. You will leverage state-of-the-art models (open source and internal research), evaluate them on representative tasks, and adapt/optimize them to meet robustness, safety, and performance needs. You will invent new algorithms where gaps exist. You’ll collaborate closely with research, controls, hardware, and product-facing teams, and your outputs will be used by downstream teams to further customize and deploy on specific robot embodiments. Key job responsibilities As an Applied Scientist in the Foundations Model team, you will: - Leverage state-of-the-art models for targeted tasks, environments, and robot embodiments through fine-tuning and optimization. - Execute rapid, rigorous experimentation with reproducible results and solid engineering practices, closing the gap between sim and real environments. - Build and run capability evaluations/benchmarks to clearly profile performance, generalization, and failure modes. - Contribute to the data and training workflow: collection/curation, dataset quality/provenance, and repeatable training recipes. - Write clean, maintainable, well commented and documented code, contribute to training infrastructure, create tools for model evaluation and testing, and implement necessary APIs - Stay current with latest developments in foundation models and robotics, assist in literature reviews and research documentation, prepare technical reports and presentations, and contribute to research discussions and brainstorming sessions. - Work closely with senior scientists, engineers, and leaders across multiple teams, participate in knowledge sharing, support integration efforts with robotics hardware teams, and help document best practices and methodologies.

[Manager, Research Science, Special Projects](https://www.amazon.jobs/jobs/10541622/manager-research-science-special-projects?cmpid=bsp-amazon-science)

US, CA, San Francisco

Innovators wanted! Are you an entrepreneur? A builder? A dreamer? This role is part of an Amazon Special Projects team that takes the company’s Think Big leadership principle to the extreme. We focus on creating entirely new products and services with a goal of positively impacting the lives of our customers. No industries or subject areas are out of bounds. If you’re interested in innovating at scale to address big challenges in the world, this is the team for you. Here at Amazon, we embrace our differences. We are committed to furthering our culture of inclusion. We have thirteen employee-led affinity groups, reaching 40,000 employees in over 190 chapters globally. We are constantly learning through programs that are local, regional, and global. Amazon’s culture of inclusion is reinforced within our 16 Leadership Principles, which remind team members to seek diverse perspectives, learn and be curious, and earn trust. Our team highly values work-life balance, mentorship and career growth. We believe striking the right balance between your personal and professional life is critical to life-long happiness and fulfillment. We care about your career growth and strive to assign projects and offer training that will challenge you to become your best.

[Applied Scientist, Sponsored Products and Brands](https://www.amazon.jobs/jobs/10539382/applied-scientist-sponsored-products-and-brands?cmpid=bsp-amazon-science)

US, WA, Seattle

About Sponsored Products and Brands The Sponsored Products and Brands (SPB) team at Amazon Ads is re-imagining the advertising landscape through generative AI technologies, revolutionizing how millions of customers discover products and engage with brands across Amazon.com and beyond. We are at the forefront of re-inventing advertising experiences, bridging human creativity with artificial intelligence to transform every aspect of the advertising lifecycle from ad creation and optimization to performance analysis and customer insights. We are a passionate group of innovators dedicated to developing responsible and intelligent AI technologies that balance the needs of advertisers, enhance the shopping experience, and strengthen the marketplace. If you're energized by solving complex challenges and pushing the boundaries of what's possible with AI, join us in shaping the future of advertising. About our team The General Shopping Intelligence (GSI) team is a highly motivated, collaborative, and fun-loving group with a strong entrepreneurial spirit and bias for action. We provide advanced real-time machine learning services that connect shoppers with the right ads across all platforms and surfaces worldwide. Through deep understanding of both shoppers and products, we help shoppers discover new products they love, enable advertisers to reach their customers most efficiently, and help Amazon continuously innovate on behalf of all customers. We are seeking a motivated Applied Scientist who loves to innovate at the intersection of customer experience, deep learning, generative AI and high-scale machine learning systems. If you're energized by solving complex challenges and pushing the boundaries of what's possible with AI, join us in shaping the future of advertising. Key job responsibilities As an Applied Scientist, you will: * Leverage Generative AI and Large Language Models (LLMs) to mine complex behavioral data, deriving deep, actionable shopper insights that identify customer experience gaps and unlock new business opportunities. * Design and develop scalable machine learning and GenAI models focused on shopper intent and preference modeling, ensuring a rapid path from prototype to production. * Partner closely with engineering teams to architect and deploy end-to-end GenAI solutions into production, integrating advanced insights directly into real-time, customer-facing systems. * Drive the scalability, efficiency, and automation of large-scale model training and real-time inference systems, pioneering the LLM infrastructure required to support next-generation GenAI workloads at Amazon Ads scale. * Design and run rigorous A/B experiments to quantify the business and customer impact of GenAI-driven shopper insights, performing advanced statistical analysis to guide iterative production rollouts. * Conduct applied research in novel generative AI techniques (e.g., fine-tuning, RAG, agentic workflows) to optimize the shopper experience and drive performance across all aspects of the Sponsored Products and Brands business.

[Applied Scientist, Agentic WorkSpaces (AAWS)](https://www.amazon.jobs/jobs/10541930/applied-scientist-agentic-workspaces-aaws?cmpid=bsp-amazon-science)

US, WA, Seattle

AWS Applied AI Solutions (AAIS) is where science meets customer obsession at scale. We build the intelligent systems that power AWS services used by millions, combining research in machine learning, agentic AI, and applied science with the operational rigor required to deliver enterprise grade experiences. Within AAIS, Amazon WorkSpaces is our cloud based virtual desktop service that delivers secure, managed computing to over one million daily users across the globe, enabling organizations to provision, manage, and scale desktops with the reliability and performance their workforce depends on. We are looking for an Applied Scientist to be part of the tiger team building the capacity modelling for Amazon WorkSpaces, owning and advancing the science behind it. You will design, build, and continuously improve the forecasting and optimization models that ensure the right compute, storage, and networking resources are available at the right time, in the right regions, at the lowest possible cost, without ever compromising the end user experience. This is a high impact individual contributor role for someone who thrives at the intersection of applied research and production systems. You will define the scientific roadmap for capacity intelligence, turning reactive provisioning into a predictive, self optimizing engine that anticipates demand before customers feel any constraint. Key job responsibilities Define and drive the scientific strategy for capacity modelling, establishing the research agenda that transforms how WorkSpaces forecasts demand, plans supply, and allocates resources across a globally distributed infrastructure. Build advanced demand forecasting models that predict workspace usage across multiple time horizons, from intraday spikes to long range growth trajectories, incorporating signals such as customer onboarding patterns, seasonal trends, regional expansion, and macroeconomic indicators. Design supply optimization frameworks that determine optimal resource placement, instance mix, and pre warming strategies, balancing availability, performance, and cost by reasoning over hardware constraints, pricing dynamics, and service level objectives. Develop causal and probabilistic models that move beyond trend extrapolation to true understanding of demand drivers, enabling the organization to distinguish organic growth from one time events, anticipate shifts in usage patterns, and quantify uncertainty in planning decisions. Architect simulation and scenario planning systems that allow business and engineering leaders to run what if analyses, stress test capacity plans against disruption scenarios, and evaluate trade offs between investment timing, risk tolerance, and customer experience. Pioneer the integration of machine learning with operations research, combining deep learning based forecasting with mathematical optimization to jointly solve the demand prediction and resource allocation problem in a way that neither discipline can achieve alone. Establish evaluation frameworks and monitoring systems that measure forecast accuracy, capacity utilization, and cost efficiency in production, creating tight feedback loops that drive continuous model improvement and build organizational trust in science driven planning. Influence the broader organization's capacity strategy by translating model outputs into actionable recommendations for leadership, identifying opportunities to extend capacity intelligence patterns to adjacent services, and mentoring scientists and engineers across the team. About the team As part of the AWS solutions organization, we have a vision to provide business applications, leveraging Amazon's unique experience and expertise, that are used by millions of companies worldwide to manage day-to-day operations. We will accomplish this by accelerating our customers' businesses through delivery of intuitive and differentiated technology solutions that solve enduring business challenges. we blend vision with curiosity and Amazon's real-world experience to build opinionated, turnkey solutions. Where customers prefer to buy over build, we become their trusted partner with solutions that are no-brainers to buy and easy to use. Diverse Experiences AWS values diverse experiences. Even if you do not meet all of the preferred qualifications and skills listed in the job description, we encourage candidates to apply. If your career is just starting, hasn’t followed a traditional path, or includes alternative experiences, don’t let it stop you from applying. Why AWS? Amazon Web Services (AWS) is the world’s most comprehensive and broadly adopted cloud platform. We pioneered cloud computing and never stopped innovating — that’s why customers from the most successful startups to Global 500 companies trust our robust suite of products and services to power their businesses. Inclusive Team Culture AWS values curiosity and connection. Our employee-led and company-sponsored affinity groups promote inclusion and empower our people to take pride in what makes us unique. Our inclusion events foster stronger, more collaborative teams. Our continual innovation is fueled by the bold ideas, fresh perspectives, and passionate voices our teams bring to everything we do. Mentorship & Career Growth We’re continuously raising our performance bar as we strive to become Earth’s Best Employer. That’s why you’ll find endless knowledge-sharing, mentorship and other career-advancing resources here to help you develop into a better-rounded professional. Work/Life Balance We value work-life harmony. Achieving success at work should never come at the expense of sacrifices at home, which is why we strive for flexibility as part of our working culture. When we feel supported in the workplace and at home, there’s nothing we can’t achieve.

[Principal Applied Scientist - AI for Life Sciences, AWS Applied AI Solutions - Life Sciences](https://www.amazon.jobs/jobs/10538102/principal-applied-scientist--ai-for-life-sciences-aws-applied-ai-solutions--life-sciences?cmpid=bsp-amazon-science)

US, WA, Seattle

As part of the AWS Applied AI Solutions organization, we have a vision to provide end user applications, leveraging Amazon's unique experience and expertise, that are used by millions of companies worldwide to manage day-to-day operations. We will accomplish this by accelerating our customers' businesses through delivery of intuitive and differentiated technology solutions that solve enduring business challenges. We blend vision with curiosity and Amazon's real-world experience to build opinionated, turnkey solutions. Where customers prefer to buy over build, we become their trusted partner with solutions that are easy to adopt and easy to use. The Team Join the next science revolution at AWS Life Sciences Applied AI Solutions, where you'll work alongside world-class scientists to build AI that transforms how therapeutics are discovered, developed, and brought to patients. We're out to revolutionize how medicines are discovered, developed, and brought to patients, powered by a new generation of AI. Our team tackles some of the hardest open problems at the intersection of frontier AI and life sciences. We apply biological foundation models, large language models, and agentic reasoning systems to life sciences problems, then put them into the hands of pharma, biotech, and diagnostics customers as applications and managed services they can fine-tune, tailor, and deploy on their own data. The science challenges are deep: how do you design agentic systems that reason correctly over complex biological, regulatory, and clinical logic? How do you enable customers to tailor foundation models to their proprietary data and get better outputs with less effort? How do you adapt models to reason faithfully in high-stakes scientific and regulatory domains? Today we're focused on two areas. In drug design, our products (including Amazon Bio Discovery) accelerate discovery by giving bench scientists AI-guided protein engineering and antibody design capabilities. In clinical trials, we're building AI that automates and optimizes regulatory and clinical development workflows. We combine frontier research with production-scale delivery to put breakthrough science into the hands of customers solving humanity's hardest problems. We value scientific rigor, encourage publication, and support conference participation. If you want to do research that ships, this is the team. The Role We are seeking an exceptional Principal Applied Scientist to set the scientific direction for our life sciences AI portfolio. You will be the scientific leader who defines research agendas, architects novel approaches, and delivers models and methods that give our customers capabilities that did not previously exist. This is a rare role that combines deep expertise in LLM reasoning and agentic AI with applied impact in life sciences. You will innovate on how large language models reason, plan, and act in complex scientific domains, while applying domain knowledge in biology to ensure models produce scientifically valid outputs. The problems span multiple fronts: - How do you build LLM-based agentic systems that correctly reason over clinical protocols, regulatory standards, and complex multi-step scientific workflows? - How do you develop model customization and training methods that let customers get state-of-the-art results from foundation models? - How do you adapt and extend protein and antibody models so customers can fine-tune on proprietary sequence data and get therapeutically relevant outputs? You will work across drug discovery (protein engineering, antibody design) and clinical trial operations (agentic automation, structured reasoning, domain adaptation). You will own end-to-end scientific solutions from research through production, and your work will directly shape the tools that thousands of scientists use daily. Key job responsibilities - Set the scientific vision and research agenda for LLM reasoning, agentic AI, and biological model customization across the portfolio - Innovate on LLM reasoning, planning, and agentic approaches for complex scientific and regulatory workflows - Develop model customization methods (fine-tuning, RLHF, retrieval augmentation, domain adaptation) that enable customers to train better models on their own data with less effort - Advance methods to adapt and extend biological foundation models for customer-specific therapeutic applications - Solve open research problems in faithful reasoning, multi-step planning, and tool use in high-stakes scientific domains - Partner with Life Sciences domain experts and customers to understand their hardest scientific challenges and translate those into tractable research problems - Publish at top-tier venues and build the team's external scientific reputation - Mentor applied scientists across the team while maintaining significant personal research contribution - Collaborate with product and engineering to ensure research translates into shipped products that serve customers at scale - Influence multi-year research roadmaps through deep scientific expertise and customer understanding A day in the life - Push a new reasoning approach into production that measurably improves outputs for a pharma customer's workflow - Design and run experiments to validate a novel fine-tuning method, then ship it as a capability customers can use immediately - Unblock a delivery milestone by diagnosing why a model is failing on a new class of inputs and implementing a fix - Meet with a customer's scientific team to scope what the next model release needs to do for them - Review a teammate's experimental results, sharpen the approach, and help get it over the finish line - Publish results from shipped work at a top venue, closing the loop between research and impact - Prototype a new idea that could become the next major capability in the product

[Principal Applied Scientist, WorkSpaces for AI Agents, Applied AI Solutions](https://www.amazon.jobs/jobs/10538705/principal-applied-scientist-workspaces-for-ai-agents-applied-ai-solutions?cmpid=bsp-amazon-science)

US, WA, Seattle

We are seeking a Principal Applied Scientist to own the scientific vision across Agentic WorkSpaces. This is a foundational role spanning the full portfolio — Personal, Applications, and Core, and the agentic surfaces (WS4Builders and WorkSpaces for Agents). You will define how we measure, improve, and guarantee the performance of AI agents and human-AI teams. A core part of the role is defining the science agenda itself — identifying which problems are most worth solving and where the highest-leverage bets lie. Directions worth exploring might include Organizational Intelligence (turning institutional knowledge into agent-consumable skills), AI Agent Experience / AiAX (agent observability and autonomous remediation), and contextual, behavioral security that adapts enforcement in real time for human and agent sessions — but these are illustrative examples, not a fixed roadmap, and many other directions are possible. You will help define which ones we pursue. The problems you will solve do not have established industry patterns. You will set the direction for the science of how AI agents and people perceive, reason about, and act reliably within computing environments at enterprise scale. Key job responsibilities - Set the long-term scientific vision: Define what best-in-class agent performance, evaluation, and learning look like across Agentic WorkSpaces — for computer-using agents and human-AI teams alike. Identify the unsolved scientific problems, chart a multi-year research roadmap, and secure buy-in from VP-level leadership. - Solve highly ambiguous, novel problems: Independently frame and deliver solutions to foundational challenges in agent perception, reasoning, evaluation, reliability, and human-AI collaboration — problems where neither the approach nor the success criteria are pre-defined. - Own the evaluation and measurement foundation: Build the benchmarks, datasets, and metrics that quantify agent and team accuracy, cost, productivity, and safety across the portfolio and diverse enterprise workflows, and that gate what we ship. - Drive cross-organizational scientific alignment: Work across partner teams (AgentCore, Bedrock model teams, Identity, Security, the MCP ecosystem) and across the Applied AI Solutions product portfolio to shape how models and agent frameworks are applied, and ensure scientific decisions compose into a coherent system. - Deliver measurable business impact: Ensure research translates to customer outcomes: higher task accuracy, lower cost-per-action, faster time-to-production, measurable productivity for human-AI teams, and the trust that lets enterprises scale agent workflows. - Raise the scientific bar: Establish rigor in experimentation, evaluation, and reproducibility. Mentor and grow senior scientists and engineers. Set the standard for applied science quality across the organization. - Advance the state of the art: Contribute to the external technical community through publications, patents, and open-source contributions that position AWS as the leader in the science of secure agent-computer interaction and human-AI teamwork. About the team AWS Applied AI Solutions' (AAIS) vision is every business innovating with Amazon AI teammates. Our mission is to build delightful AI solutions that improve human capabilities and business outcomes. The Agentic WorkSpaces organization within AAIS envisions a world where people, teams, and AI collaborate securely from anywhere to create unprecedented value for every organization. We build lovable products that empower every business to unlock the full potential of human-AI teamwork, driving smarter decisions, greater creativity, more value, and faster innovation with confidence. Amazon Agentic WorkSpaces (AAWS) is building the world's most lovable, secure, and trusted always-on workspace where AI agents and humans work as partners behind enterprise-grade security. Our portfolio spans persistent desktops (Personal), application streaming (Applications), and Core, and is evolving into the governed operating environment for the hybrid workforce: humans get AI-native desktops for their role, and agents get governed desktops scoped to their task, with administrators managing both as one. This surface includes WS4Builders (an AI-native environment for builders) and WorkSpaces for Agents (W4A) — enabling AI agents to work the way humans do, with access to real applications, real interfaces, and real computing environments. Enterprises want to use AI agents for critical business workloads that touch legacy desktop applications and mainframes, yet 75% of organizations run legacy applications that lack modern APIs, and 90% of corporate data remains locked in systems never designed for agents. Agentic WorkSpaces solves this: it gives enterprises a secure, governed environment where agents and humans operate both legacy and modern applications directly, just as an employee would, without costly migrations.

[Senior Manager, Applied Science](https://www.amazon.jobs/jobs/10537980/senior-manager-applied-science?cmpid=bsp-amazon-science)

US, WA, Seattle

We are seeking a Senior Manager, Applied Science to build and lead the science organization across Agentic WorkSpaces. This is a foundational leadership role spanning the full portfolio — Personal, Applications, and Core, and the agentic surfaces (WS4Builders and WorkSpaces for Agents). You will hire, grow, and lead a team of applied scientists who define how we measure and improve the performance of AI agents and human-AI teams. A core part of the role is defining the science agenda itself — identifying which problems are most worth solving and where the highest-leverage bets lie. Directions worth exploring might include Organizational Intelligence (turning institutional knowledge into agent-consumable skills), AI Agent Experience / AiAX (agent observability and autonomous remediation), and contextual, behavioral security that adapts enforcement in real time for human and agent sessions — but these are illustrative examples, not a fixed roadmap, and many other directions are possible. You and your team will define which ones we pursue. The problems your team will solve do not have established industry patterns. You will set the scientific direction and build the team that determines how AI agents and people perceive, reason about, and act reliably within computing environments at enterprise scale. What You Will Do Build and lead the applied science team. Hire, develop, and retain a high-caliber team of applied scientists spanning the Agentic WorkSpaces portfolio. Set the bar for scientific talent, create the growth paths, and build the culture that makes AAWS a destination for the best agent and human-AI researchers. Own the science strategy across the portfolio. Direct the research agenda for how we measure and improve agents and human-AI teams: the benchmarks, task suites, and metrics (accuracy, cost-per-task, task completion, productivity) that turn subjective "it works" judgments into rigorous, reproducible measurement that gates what we ship. Define and drive high-leverage research directions. Work with your team to identify the problems most worth solving and shape the science agenda. Directions worth exploring might include how agents combine deterministic tool use (MCP) with visual reasoning from computer use; Organizational Intelligence and workflow learning (learning from expert recordings, voice annotations, and SOPs); and AI Agent Experience / AiAX (detecting when agents are stuck or degrading productivity and autonomously remediating) — these are illustrative starting points, and your team will weigh them against many other possibilities. Translate science into shipped product. Partner with engineering, product, and program leaders to move models, evaluation, and learning systems from prototype into a decade-old production service operating at massive scale, without compromising the reliability that customers depend on. Represent science in leadership and to customers. Be the scientific voice in org-level planning and roadmap decisions across AAWS, and engage directly with enterprise customers on how agent performance, safety, and human-AI productivity are measured and earned. Key job responsibilities Build and lead the applied science team. Hire, develop, and retain a high-caliber team of applied scientists spanning the Agentic WorkSpaces portfolio. Set the bar for scientific talent, create the growth paths, and build the culture that makes AAWS a destination for the best agent and human-AI researchers. Own the science strategy across the portfolio. Direct the research agenda for how we measure and improve agents and human-AI teams: the benchmarks, task suites, and metrics (accuracy, cost-per-task, task completion, productivity) that turn subjective "it works" judgments into rigorous, reproducible measurement that gates what we ship. Define and drive high-leverage research directions. Work with your team to identify the problems most worth solving and shape the science agenda. Directions worth exploring might include how agents combine deterministic tool use (MCP) with visual reasoning from computer use; Organizational Intelligence and workflow learning (learning from expert recordings, voice annotations, and SOPs); and AI Agent Experience / AiAX (detecting when agents are stuck or degrading productivity and autonomously remediating) — these are illustrative starting points, and your team will weigh them against many other possibilities. Translate science into shipped product. Partner with engineering, product, and program leaders to move models, evaluation, and learning systems from prototype into a decade-old production service operating at massive scale, without compromising the reliability that customers depend on. Represent science in leadership and to customers. Be the scientific voice in org-level planning and roadmap decisions across AAWS, and engage directly with enterprise customers on how agent performance, safety, and human-AI productivity are measured and earned. Set the long-term scientific vision and team strategy: Define what best-in-class agent performance, evaluation, and learning look like across Agentic WorkSpaces — for computer-using agents and human-AI teams alike. Chart a multi-year research roadmap, and build the team and plan to deliver it. Secure buy-in from VP-level leadership. Hire and grow scientific talent: Own recruiting, calibration, development, and retention for the science team. Mentor scientists toward senior and principal scope, and raise the scientific bar across the organization. Direct research on highly ambiguous, novel problems: Guide the team through foundational challenges in agent perception, reasoning, evaluation, reliability, and human-AI collaboration — problems where neither the approach nor the success criteria are pre-defined. Drive cross-organizational alignment: Work across partner teams (AgentCore, Bedrock model teams, Identity, Security, the MCP ecosystem) and across the Applied AI Solutions product portfolio, with product and engineering leadership, to ensure scientific decisions compose into a coherent product. Deliver measurable business impact: Ensure your team's research translates to customer outcomes: higher task accuracy, lower cost-per-action, faster time-to-production, measurable productivity for human-AI teams, and the trust that lets enterprises scale agent workflows. Establish scientific rigor and operational excellence: Set the standard for experimentation, evaluation, and reproducibility, and the mechanisms that keep the science organization productive and accountable. Advance the state of the art: Enable and champion contributions to the external technical community through publications, patents, and open-source work that position AWS as the leader in the science of secure agent-computer interaction and human-AI teamwork. About the team AWS Applied AI Solutions' (AAIS) vision is every business innovating with Amazon AI teammates. Our mission is to build delightful AI solutions that improve human capabilities and business outcomes. The Agentic WorkSpaces organization within AAIS envisions a world where people, teams, and AI collaborate securely from anywhere to create unprecedented value for every organization. We build lovable products that empower every business to unlock the full potential of human-AI teamwork, driving smarter decisions, greater creativity, more value, and faster innovation with confidence. Amazon Agentic WorkSpaces (AAWS) is building the world's most lovable, secure, and trusted always-on workspace where AI agents and humans work as partners behind enterprise-grade security. Our portfolio spans persistent desktops (Personal), application streaming (Applications), and Core, and is evolving into the governed operating environment for the hybrid workforce: humans get AI-native desktops for their role, and agents get governed desktops scoped to their task, with administrators managing both as one. This surface includes WS4Builders (an AI-native environment for builders) and WorkSpaces for Agents (W4A) — enabling AI agents to work the way humans do, with access to real applications, real interfaces, and real computing environments. Enterprises want to use AI agents for critical business workloads that touch legacy desktop applications and mainframes, yet 75% of organizations run legacy applications that lack modern APIs, and 90% of corporate data remains locked in systems never designed for agents. Agentic WorkSpaces solves this: it gives enterprises a secure, governed environment where agents and humans operate both legacy and modern applications directly, just as an employee would, without costly migrations.

[Applied Scientist II, Amazon Shipping](https://www.amazon.jobs/jobs/10537213/applied-scientist-ii-amazon-shipping?cmpid=bsp-amazon-science)

IN, HR, Gurugram

Work on ML teams building large-scale forecasting and optimization systems that power Amazon’s global transportation network and directly impact customer experience and cost. As an Applied Scientist II, you will set scientific direction, mentor applied scientists, and partner with engineering and product leaders to deliver production-grade ML solutions at massive scale. Key job responsibilities 1. Lead and grow a high-performing team of Applied Scientists, providing technical guidance, mentorship, and career development. 2. Define and own the scientific vision and roadmap for ML solutions powering large-scale transportation planning and execution. 3. Guide model and system design across a range of techniques, including tree-based models, deep learning (LSTMs, transformers), LLMs, and reinforcement learning. 4. Ensure models are production-ready, scalable, and robust through close partnership with stakeholders. Partner with Product, Operations, and Engineering leaders to enable proactive decision-making and corrective actions. 5. Own end-to-end business metrics, directly influencing customer experience, cost optimization, and network reliability. 6. Help contribute to the broader ML community through publications, conference submissions, and internal knowledge sharing. A day in the life Your day includes reviewing model performance and business metrics, guiding technical design and experimentation, mentoring scientists, and driving roadmap execution. You’ll balance near-term delivery with long-term innovation while ensuring solutions are robust, interpretable, and scalable. Ultimately, your work helps improve delivery reliability, reduce costs, and enhance the customer experience at massive scale.

[See more jobs](https://www.amazon.science/careers)

[![Image 59: Amazon Science](https://cdn.amazon.science/ce/51/a0ecec814b0894e11c0f22dbcc17/amazonscience-white.svg)](https://www.amazon.science/)

*   [About](https://www.amazon.science/about)  
*   [Research areas](https://www.amazon.science/research-areas)  
*   [Blog](https://www.amazon.science/blog)  
*   [Publications](https://www.amazon.science/publications)  
*   [Conferences](https://www.amazon.science/conferences-and-events)  
*   [Code and datasets](https://www.amazon.science/code-and-datasets)  
*   [Academia](https://www.amazon.science/academic-engagements)  
*   [Amazon News](https://www.aboutamazon.com/?utm_source=amazon_science&utm_medium=footer&utm_campaign=evergreen_homepage)  
*   [Amazon Developer](https://developer.amazon.com/)  
*   [Amazon Web Services](https://aws.amazon.com/blogs)  
*   [Awards and recognitions](https://www.amazon.science/awards-and-recognitions)  
*   [Newsletter](https://www.linkedin.com/newsletters/7185109507369226240/)  
*   [Careers](https://www.amazon.science/careers)  
*   [FAQs](https://www.amazon.science/faqs)  

![Image 60: View from space of a connected network around planet Earth representing the Internet of Things.](https://cdn.amazon.science/dims4/default/8c95e42/2147483647/strip/true/crop/1465x1277+227+0/resize/70x61!/quality/90/?url=https%3A%2F%2Famzn-science-production-science.s3.us-east-1.amazonaws.com%2Fscience%2F20%2Fc4%2Fc36de9f643dab18e2f27ea071590%2Famazon-science-newsletter-project-kuiper.jpg)

[Get more from Amazon Science](https://www.amazon.science/newsletter)

Subscribe to our newsletter

[Amazon.com](https://www.amazon.com/) | [Conditions of Use](https://www.amazon.com/gp/help/customer/display.html/ref=footer_cou?ie=UTF8&nodeId=508088) | [Privacy](https://www.amazon.com/gp/help/customer/display.html?nodeId=468496) | © 1996-2026 Amazon.com, Inc. or its affiliates

Social

*   [bluesky](https://bsky.app/profile/amazon.science)
*   [threads](https://www.threads.com/@amazonscience)
*   [twitter](https://x.com/AmazonScience)
*   [instagram](https://www.instagram.com/AmazonScience/)
*   [youtube](https://www.youtube.com/c/AmazonScience)
*   [facebook](https://www.facebook.com/AmazonScience)
*   [linkedin](https://www.linkedin.com/showcase/AmazonScience)
*   [github](https://github.com/amazon-science)
*   [rss](https://www.amazon.science/index.rss)

<!-- media:svg src="https://cdn.amazon.science/7c/fb/3a915dcf44b3ae2cac79acf280d8/automated-reasoning.svg" -->

<!-- media:svg src="https://cdn.amazon.science/26/0a/47bb5de4438483f43551f13963d9/cloud-and-systems.svg" -->

<!-- media:svg src="https://cdn.amazon.science/6a/16/a6e53bfe46ceab77d292a8cea6af/computer-vision.svg" -->

<!-- media:svg src="https://cdn.amazon.science/2e/8b/017e23db42f0a6e2c4e12a24f2aa/conversational-ai-and-natural-language-processing.svg" -->

<!-- media:svg src="https://cdn.amazon.science/c3/a9/4eaa12b34e018438b648da0984c8/economics.svg" -->

<!-- media:svg src="https://cdn.amazon.science/8e/8b/3f08e7fd495c9f3ca8667d280825/information-and-knowledge-management.svg" -->

<!-- media:svg src="https://cdn.amazon.science/9b/85/f1a70d944530ab25b4100eca8ae6/machine-learning.svg" -->

<!-- media:svg src="https://cdn.amazon.science/af/26/afe9cd8041779f0d098ccd7cc686/operations-research-and-optimization.svg" -->

<!-- media:svg src="https://cdn.amazon.science/30/fa/d9b66fce484290127e3e4319f45e/quantum-technologies.svg" -->

<!-- media:svg src="https://cdn.amazon.science/5d/b0/310093db4e0da3496b9bac97b17f/robotics.svg" -->

<!-- media:svg src="https://cdn.amazon.science/91/f9/abec27f74777b60a69e3e4280228/search-and-information-retrieval.svg" -->

<!-- media:svg src="https://cdn.amazon.science/fc/ba/b7df3c284e6b9afc3487753a1bad/sustainability.svg" -->
