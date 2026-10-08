from __future__ import annotations

import re
from dataclasses import dataclass


# The detector deliberately keeps the older Hades fan-service vocabulary while
# adding newer signals. Multiple categories can match the same message.
PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "fan_command": (
        re.compile(
            r"\b(?:step\s+on\s+me|step\s+on\s+my\s+face|dominate\s+me|sit\s+on\s+me|"
            r"pin\s+me\s+down|crush\s+me|ruin\s+me|destroy\s+me|"
            r"put\s+me\s+under\s+your\s+heel|put\s+me\s+in\s+my\s+place|"
            r"make\s+me\s+beg|make\s+me\s+ask\s+properly|make\s+me\s+ask\s+nicely|"
            r"make\s+me\s+obey|make\s+me\s+kneel|make\s+me\s+behave|"
            r"tell\s+me\s+what\s+to\s+do|command\s+me|order\s+me\s+around|"
            r"boss\s+me\s+around|walk\s+all\s+over\s+me)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:i\s+wish\s+you(?:'d|\s+would)\s+put\s+me\s+in\s+my\s+place|"
            r"i\s+would\s+let\s+you\s+command\s+me)\b",
            re.I,
        ),
    ),
    "playful_dominance": (
        re.compile(
            r"\b(?:good\s+(?:boy|girl)|bad\s+(?:boy|girl)|yes\s+ma(?:'am|am)|yes\s+mistress|"
            r"yes\s+lady|make\s+me\s+say\s+please|i(?:'ll|\s+will)\s+behave|"
            r"i(?:'m|\s+am)\s+behaving|i\s+surrender|i\s+yield)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:kneel|obey|submit|beg|behave)\b.{0,40}\b(?:hades|you|ma'am|her)\b",
            re.I,
        ),
    ),
    "romantic": (
        re.compile(
            r"\b(?:marry\s+me|be\s+my\s+wife|be\s+my\s+girlfriend|date\s+me|take\s+me\s+out|go\s+out\s+with\s+me|want\s+to\s+go\s+out|go\s+out\s+and\s+eat|go\s+out\s+for\s+(?:food|dinner|lunch|coffee)|want\s+to\s+eat\s+(?:with\s+me|together)|"
            r"take\s+you\s+out|go\s+on\s+a\s+date|want\s+to\s+go\s+on\s+a\s+date|wanna\s+go\s+out\s+for\s+(?:a|an)\s+date|"
            r"go\s+out\s+with\s+me|romance\s+me|i\s+(?:have\s+a\s+crush|am\s+crushing)\s+on\s+you|"
            r"i(?:'m|\s+am)\s+(?:in\s+love|down\s+bad|smitten|head\s+over\s+heels)\s+"
            r"(?:for|with)\s+you|i\s+am\s+obsessed\s+with\s+you|"
            r"you(?:'re|\s+are)\s+(?:my\s+wife|the\s+one\s+for\s+me)|"
            r"my\s+wife|my\s+beloved|one\s+for\s+me|my\s+favorite\s+person|"
            r"i(?:'d|\s+would)\s+marry\s+you|i(?:'d|\s+would)\s+date\s+you|"
            r"you\s+have\s+my\s+heart)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:have|grab|share|join\s+me\s+for)\s+(?:some\s+)?(?:dinner|lunch|breakfast|coffee)\s+"
            r"(?:with\s+me|together)|\b(?:dinner|lunch|breakfast|coffee)\s+with\s+me\b",
            re.I,
        ),
    ),
    "social_invitation": (
        re.compile(
            r"\b(?:want\s+to\s+go\s+out|wanna\s+go\s+out(?!\s+for\s+(?:a|an)\s+date)|"
            r"want\s+to\s+hang\s+out(?:\s+with\s+me|\s+together)?|"
            r"wanna\s+hang\s+out(?:\s+with\s+me|\s+together)?|"
            r"come\s+out\s+with\s+me|come\s+hang\s+out\s+with\s+me|"
            r"spend\s+time\s+with\s+me|go\s+somewhere\s+with\s+me|"
            r"join\s+me\s+(?:for\s+)?(?:dinner|lunch|breakfast|coffee)|"
            r"grab\s+(?:dinner|lunch|breakfast|coffee)\s+with\s+me|"
            r"eat\s+(?:with\s+me|together)|have\s+(?:dinner|lunch|breakfast|coffee)\s+with\s+me)\b",
            re.I,
        ),
    ),
    "affection": (
        re.compile(
            r"\b(?:kiss(?:\s+me)?|give\s+me\s+a\s+kiss|hug(?:\s+me)?|cuddle(?:\s+me)?|hold\s+me|"
            r"hold\s+my\s+hand|take\s+my\s+hand|pat\s+my\s+head|headpats?|headpat(?:\s+me)?|"
            r"pet\s+me|embrace\s+me|comfort\s+me|stay\s+close\s+to\s+me|stay\s+with\s+me|"
            r"sit\s+next\s+to\s+me|sit\s+with\s+me|sit\s+beside\s+me|come\s+sit\s+with\s+me|"
            r"carry\s+me|let\s+me\s+hold\s+you|let\s+me\s+hold\s+your\s+hand|"
            r"let\s+me\s+lean\s+on\s+you|let\s+me\s+rest\s+on\s+your\s+shoulder|"
            r"give\s+me\s+a\s+forehead\s+kiss|kiss\s+my\s+forehead|kiss\s+my\s+cheek|"
            r"kiss\s+my\s+hand|hold\s+me\s+close|pull\s+me\s+closer|"
            r"let\s+me\s+cuddle|sleep\s+on\s+(?:your|ur)\s+(?:thighs?|lap)|"
            r"rest\s+(?:my|your)\s+head\s+on\s+(?:your|my)\s+(?:lap|thighs?)|"
            r"(?:sit|lie)\s+on\s+(?:your|my)\s+lap|take\s+a\s+nap\s+(?:on|with)\s+you)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:play\s+with\s+my\s+hair|stroke\s+my\s+hair|brush\s+my\s+hair|"
            r"fix\s+my\s+hair|fix\s+my\s+collar|touch\s+my\s+cheek|kiss\s+my\s+cheek|"
            r"cup\s+my\s+face|hold\s+my\s+face|boop\s+my\s+nose|"
            r"touch\s+foreheads?|rest\s+your\s+forehead\s+against\s+mine)\b",
            re.I,
        ),
        re.compile(r"\b(?:love\s+you|i\s+adore\s+you|i\s+love\s+you|i\s+miss\s+you)\b", re.I),
    ),

    "scent_and_proximity": (
        re.compile(
            r"\b(?:sniff(?:ing)?|whiff(?:ing)?|smell(?:ing)?)\b.{0,45}\b(?:you|your|ur|hades|her)\b|"
            r"\b(?:you|your|ur|hades|her)\b.{0,45}\b(?:scent|aroma|perfume|smell|sniff|whiff)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:let|can|may|could|would)\s+me\s+(?:take\s+a\s+)?"
            r"(?:whiff|sniff|smell)\b.{0,45}\b(?:you|your|ur|hades|her)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:your|ur)\s+(?:scent|aroma|perfume)\b|"
            r"\b(?:sniff|smell|whiff)\s+(?:behind\s+)?(?:your|ur)\b",
            re.I,
        ),
    ),

    "captivated": (
        re.compile(
            r"\b(?:you\s+have\s+me\s+under\s+your\s+spell|you've\s+got\s+me\s+under\s+your\s+spell|"
            r"you\s+have\s+me\s+wrapped\s+around\s+your\s+finger|you've\s+got\s+me\s+wrapped\s+around\s+your\s+finger|"
            r"putty\s+in\s+your\s+hands|you\s+have\s+me\s+mesmerized|you've\s+got\s+me\s+mesmerized|"
            r"you\s+live\s+rent[- ]free\s+in\s+my\s+head|you(?:'re|\s+are)\s+living\s+rent[- ]free\s+in\s+my\s+head|"
            r"i\s+can't\s+stop\s+thinking\s+about\s+you|i\s+can't\s+get\s+you\s+out\s+of\s+my\s+head|"
            r"you\s+are\s+so\s+captivating|you're\s+so\s+captivating|you\s+are\s+mesmerizing|you're\s+mesmerizing|"
            r"you\s+have\s+my\s+full\s+attention|you've\s+got\s+my\s+full\s+attention)\b",
            re.I,
        ),
    ),

    "devotion": (
        re.compile(
            r"\b(?:i\s+am\s+devoted\s+to\s+you|i'm\s+devoted\s+to\s+you|"
            r"your\s+devoted\s+(?:little\s+)?lamb|your\s+loyal\s+(?:little\s+)?lamb|"
            r"i'd\s+serve\s+you|i\s+will\s+serve\s+you|let\s+me\s+serve\s+you|"
            r"i'd\s+worship\s+you|i\s+would\s+worship\s+you|worship\s+you|"
            r"i\s+am\s+at\s+your\s+feet|i'm\s+at\s+your\s+feet|"
            r"all\s+for\s+you|anything\s+for\s+you|your\s+faithful\s+little\s+lamb)\b",
            re.I,
        ),
    ),

    "playful_jealousy": (
        re.compile(
            r"\b(?:don't\s+make\s+me\s+jealous|are\s+you\s+flirting\s+with\s+(?:everyone|someone\s+else)|"
            r"am\s+i\s+the\s+only\s+one|am\s+i\s+your\s+favorite|"
            r"are\s+you\s+giving\s+(?:them|her|him)\s+that\s+look|"
            r"what\s+about\s+me|save\s+some\s+attention\s+for\s+me|"
            r"you're\s+making\s+me\s+jealous|you'?re\s+making\s+me\s+jealous)\b",
            re.I,
        ),
    ),
    "admiration": (
        re.compile(
            r"\b(?:(?:you(?:'re|\s+are)|ur|u(?:\s+r)?)\s+(?:so+\s+|very\s+|really\s+|extremely\s+|incredibly\s+|"
            r"absurdly\s+|unfairly\s+)?(?:gorgeous|beautiful|pretty|stunning|hot|cute|adorable|"
            r"elegant|graceful|refined|classy|perfect|amazing|majestic|breathtaking|unreal|"
            r"dangerously\s+attractive|ridiculously\s+pretty|good[- ]looking)|"
            r"(?:you\s+look|u\s+look)\s+(?:gorgeous|beautiful|pretty|stunning|hot|cute|elegant|amazing|unfair)|"
            r"you\s+(?:look|are)\s+like\s+a\s+(?:dream|temptation|snack)|"
            r"wife\s+material|my\s+gorgeous\s+woman|my\s+favorite\s+woman|"
            r"you\s+are\s+unfair|you're\s+unfair|how\s+are\s+you\s+this\s+pretty|"
            r"you\s+caught\s+my\s+eye|you\s+drew\s+my\s+attention|you\s+have\s+my\s+attention|"
            r"(?:you(?:\'re|\s+are)|ur)\s+(?:the\s+one\s+who\s+)?(?:drew|caught)\s+my\s+attention(?:\s+to\s+(?:you|u))?|"
            r"you\s+keep\s+(?:catching|getting)\s+my\s+attention|you\s+keep\s+catching\s+my\s+eye|"
            r"you(?:'ve|\s+have)\s+got\s+me\s+(?:looking|staring)|"
            r"you\s+have\s+me\s+(?:looking|staring)|you\s+had\s+me\s+(?:looking|staring)|"
            r"i\s+(?:was|am)\s+drawn\s+to\s+you|i\s+keep\s+(?:looking|staring)\s+at\s+you|"
            r"i\s+(?:noticed|noticed\s+you)\s+(?:first|right\s+away)|hard\s+not\s+to\s+(?:look|stare)\s+at\s+you|"
            r"hard\s+to\s+look\s+away|can't\s+look\s+away|cannot\s+look\s+away|"
            r"i\s+can't\s+stop\s+looking|i\s+can't\s+look\s+away)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:such|so\s+much)\s+(?:elegance|grace|poise|class|presence)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:where\s+did|where\s+does)\s+(?:this|that|your)\s+"
            r"(?:elegance|grace|maternal|motherly)"
            r"(?:\s+and\s+(?:elegance|grace|maternal|motherly|maternal\s+traits|motherly\s+traits))?"
            r"\s+(?:come|come\s+from|originate)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:elegance|grace|poise)\s+and\s+(?:maternal|motherly)\s+(?:traits|qualities)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:your|that)\s+(?:smile|voice|eyes|outfit|dress|hair|presence)\s+"
            r"(?:is|are)\s+(?:gorgeous|beautiful|perfect|unfair|everything|stunning)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:absolute\s+beauty|what\s+a\s+beauty|you(?:'re|\s+are)\s+seriously\s+(?:pretty|beautiful|hot|gorgeous)|"
            r"ur\s+seriously\s+(?:pretty|beautiful|hot|gorgeous))\b",
            re.I,
        ),
        re.compile(
            r"\b(?:i\s+could\s+(?:stare|look)\s+at\s+you\s+all\s+day|i\s+could\s+listen\s+to\s+(?:you|your\s+voice)\s+all\s+day|"
            r"your\s+voice\s+is\s+(?:dangerous|beautiful|addictive|mesmerizing|gorgeous)|"
            r"the\s+way\s+you\s+speak\s+is\s+(?:dangerous|beautiful|mesmerizing)|"
            r"your\s+smile\s+should\s+be\s+illegal|you\s+should\s+be\s+illegal\s+to\s+look\s+at|"
            r"you\s+are\s+such\s+a\s+distraction|you're\s+such\s+a\s+distraction|"
            r"you\s+make\s+it\s+hard\s+to\s+focus|you've\s+made\s+me\s+forget\s+what\s+i\s+was\s+saying|"
            r"i\s+forgot\s+what\s+i\s+was\s+saying\s+because\s+of\s+you|"
            r"i\s+can'?t\s+look\s+away\s+from\s+you)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:you(?:'re|\s+are)|ur)\s+(?:(?:exactly|totally|definitely|absolutely)\s+)?my\s+type\b|"
            r"\bhades\s+(?:is\s+)?(?:(?:exactly|totally|definitely|absolutely)\s+)?my\s+type\b",
            re.I,
        ),
    ),
    "voice_and_eye_contact": (
        re.compile(
            r"\b(?:say\s+my\s+name(?:\s+again)?|let\s+me\s+hear\s+your\s+voice|"
            r"i\s+want\s+to\s+hear\s+your\s+voice|whisper\s+my\s+name|"
            r"look\s+into\s+my\s+eyes|look\s+me\s+in\s+the\s+eyes|hold\s+my\s+gaze|"
            r"keep\s+eye\s+contact|don't\s+break\s+eye\s+contact)\b",
            re.I,
        ),
    ),
    "praise": (
        re.compile(
            r"\b(?:praise\s+me|tell\s+me\s+i(?:'m|\s+am)\s+good|say\s+i(?:'m|\s+am)\s+good|"
            r"call\s+me\s+(?:a\s+good\s+)?(?:boy|girl|lamb)|give\s+me\s+some\s+praise|"
            r"compliment\s+me)\b",
            re.I,
        ),
    ),
    "playful_fandom": (
        re.compile(
            r"\b(?:mommy|my\s+queen|goddess|adopt\s+me|own\s+me|"
            r"please\s+notice\s+me|i\s+want\s+your\s+attention|"
            r"call\s+me\s+little\s+lamb|your\s+little\s+lamb|i(?:'m|\s+am)\s+your\s+little\s+lamb|"
            r"call\s+me\s+your\s+favorite|your\s+favorite\s+little\s+lamb|"
            r"let\s+me\s+serve\s+you|make\s+me\s+your\s+puppet|"
            r"keep\s+me\s+with\s+you|make\s+me\s+one\s+of\s+your\s+favorites|"
            r"call\s+me\s+(?:good\s+)?(?:girl|boy))\b",
            re.I,
        ),
    ),
    "puppet_fantasy": (
        re.compile(
            r"\b(?:make\s+me\s+your\s+puppet|turn\s+me\s+into\s+your\s+puppet|be\s+your\s+puppet|"
            r"make\s+me\s+a\s+puppet|pull\s+my\s+strings|play\s+with\s+my\s+strings|"
            r"put\s+strings\s+on\s+me|let\s+me\s+be\s+your\s+puppet)\b",
            re.I,
        ),
    ),
    "flustered": (
        re.compile(
            r"\b(?:stop\s+making\s+me\s+blush|you(?:'re|\s+are)\s+making\s+me\s+blush|"
            r"you\s+make\s+me\s+blush|i(?:'m|\s+am)\s+blushing|i(?:'m|\s+am)\s+folding|"
            r"i(?:'m|\s+am)\s+weak\s+for\s+you|"
            r"i\s+cannot\s+think\s+straight|you'?ve\s+got\s+me\s+speechless|i(?:'m|\s+am)\s+speechless|"
            r"you\s+make\s+me\s+nervous|i(?:'m|\s+am)\s+folding|i\s+folded|you\s+got\s+me\s+folding|i\s+feel\s+weak\s+for\s+you)\b",
            re.I,
        ),
    ),
    "flirtation": (
        re.compile(
            r"\b(?:somewhere\s+(?:else\s+)?(?:very\s+)?private|somewhere\s+quiet|"
            r"somewhere\s+secluded|away\s+from\s+(?:prying|watching)\s+eyes|"
            r"where\s+(?:no\s+one|nobody)\s+can\s+(?:see|hear)\s+us|"
            r"just\s+the\s+two\s+of\s+us|just\s+us|behind\s+closed\s+doors|"
            r"keep\s+this\s+between\s+us|no\s+one\s+has\s+to\s+know|out\s+of\s+(?:sight|earshot)|"
            r"when\s+we'?re\s+alone|when\s+no\s+one'?s\s+around|after\s+dark|"
            r"when\s+the\s+others\s+are\s+gone|meet\s+me\s+somewhere|come\s+find\s+me|"
            r"come\s+closer\s+and\s+see|closer\s+than\s+that|somewhere\s+very\s+private)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:fine|good|gorgeous|beautiful|pretty|stunning|handsome|good[- ]looking|"
            r"fine[- ]looking|dangerously\s+attractive)\s+(?:like\s+)?(?:a\s+)?"
            r"(?:fine\s+)?(?:wine|vintage|dream|snack|temptation)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:aged\s+like\s+(?:fine\s+)?wine|like\s+fine\s+wine|fine\s+wine|"
            r"good\s+enough\s+to\s+tempt\s+me|you'?re\s+(?:a\s+)?temptation|"
            r"you\s+look\s+dangerous|you'?re\s+dangerous\s+(?:and\s+)?pretty|"
            r"you'?re\s+dangerously\s+attractive)\b",
            re.I,
        ),
        re.compile(
            r"(?:not|ain't|am\s+not|i\s+am\s+not)\s+(?:backing|gonna\s+back|going\s+to\s+back)\s+down"
            r".{0,120}\b(?:fine|good|gorgeous|beautiful|pretty|stunning|handsome|"
            r"good[- ]looking|fine[- ]looking|tempting|dangerously\s+attractive)\b",
            re.I | re.S,
        ),
        re.compile(
            r"\b(?:you'?re|you\s+are|ur)\s+(?:fine|good[- ]looking|fine[- ]looking|"
            r"a\s+fine\s+wine|a\s+whole\s+glass\s+of\s+fine\s+wine|dangerously\s+attractive|"
            r"too\s+pretty\s+for\s+my\s+own\s+good)\b",
            re.I,
        ),
        re.compile(
            r"\b(?:don't\s+tempt\s+me|are\s+you\s+tempting\s+me|you\s+know\s+what\s+you'?re\s+doing|"
            r"you\s+know\s+exactly\s+what\s+you'?re\s+doing|is\s+that\s+an\s+invitation|"
            r"should\s+i\s+take\s+that\s+as\s+an\s+invitation|are\s+you\s+inviting\s+me|"
            r"you\s+sure\s+you\s+can\s+handle\s+me|can\s+you\s+handle\s+me|"
            r"don't\s+look\s+at\s+me\s+like\s+that|stop\s+looking\s+at\s+me\s+like\s+that|"
            r"you're\s+making\s+this\s+too\s+easy|you'?re\s+asking\s+for\s+trouble|"
            r"you'?re\s+trouble|you\s+are\s+trouble|what\s+are\s+you\s+doing\s+to\s+me|"
            r"what\s+have\s+you\s+done\s+to\s+me|is\s+this\s+a\s+trap|"
            r"such\s+a\s+tease|quit\s+teasing\s+me|are\s+you\s+flirting\s+with\s+me|"
            r"are\s+you\s+trying\s+to\s+flirt)\b",
            re.I,
        ),
    ),
    "rivalry_banter": (
        re.compile(
            r"\b(?:old\s+hag|old\s+witch|you\s+really\s+are\s+an?\s+old\s+hag|"
            r"you\s+won\s+the\s+battle|i\s+won\s+the\s+battle|"
            r"(?:yet\s+to|have\s+yet\s+to)\s+win\s+the\s+war|"
            r"the\s+war\s+isn'?t\s+over|this\s+isn'?t\s+over|"
            r"we'?ll\s+see\s+who\s+wins|you\s+think\s+you'?ve\s+won|"
            r"not\s+so\s+fast|my\s+turn\s+next|your\s+move)\b",
            re.I,
        ),
    ),
    "attention_seek": (
        re.compile(
            r"\b(?:give\s+me\s+attention|give\s+me\s+your\s+attention|pay\s+attention\s+to\s+me|"
            r"look\s+at\s+me|notice\s+me|don't\s+ignore\s+me|please\s+notice\s+me|"
            r"i\s+need\s+your\s+attention|i\s+want\s+your\s+attention|pick\s+me|choose\s+me|"
            r"look\s+my\s+way)\b",
            re.I,
        ),
    ),
    "rivalry_banter": (
        re.compile(
            r"\b(?:old\s+hag|old\s+witch|you\s+really\s+are\s+an?\s+old\s+hag|"
            r"you\s+won\s+the\s+battle|i\s+won\s+the\s+battle|"
            r"(?:yet\s+to|have\s+yet\s+to)\s+win\s+the\s+war|"
            r"the\s+war\s+isn'?t\s+over|this\s+isn'?t\s+over|"
            r"we'?ll\s+see\s+who\s+wins|you\s+think\s+you'?ve\s+won|"
            r"not\s+so\s+fast|my\s+turn\s+next|your\s+move)\b",
            re.I,
        ),
    ),
    "teasing_challenge": (
        re.compile(
            r"\b(?:prove\s+it|try\s+me|bet\s+you\s+can't|bet\s+you\s+won't|make\s+me\s+blush|"
            r"make\s+me\s+flustered|fluster\s+me|think\s+you\s+can\s+handle\s+me|"
            r"can\s+you\s+handle\s+me|your\s+move|your\s+turn|go\s+on\s+then|"
            r"hard\s+to\s+get|playing\s+hard\s+to\s+get|making\s+me\s+work\s+for\s+it|"
            r"short\s+end\s+of\s+the\s+stick)\b",
            re.I,
        ),
    ),
}

FANSERVICE_PATTERNS = PATTERNS


@dataclass(frozen=True, slots=True)
class FanserviceAnalysis:
    primary_category: str | None
    secondary_categories: tuple[str, ...]
    intensity: str
    confidence: str


_CATEGORY_PRIORITY = (
    "fan_command",
    "playful_dominance",
    "romantic",
    "social_invitation",
    "affection",
    "scent_and_proximity",
    "captivated",
    "devotion",
    "playful_jealousy",
    "admiration",
    "voice_and_eye_contact",
    "praise",
    "playful_fandom",
    "puppet_fantasy",
    "flustered",
    "flirtation",
    "attention_seek",
    "teasing_challenge",
    "rivalry_banter",
)

_CATEGORY_GUIDANCE = {
    "fan_command": (
        "Treat the user's exaggerated request as playful fan teasing rather than a literal command. "
        "Hades will often tease, mock the user's lack of composure, issue a playful challenge, or use effortless mock-authority. "
        "She may reward the boldness with amused approval instead of always escalating the fantasy. "
        "A restrained flirt is optional, not required. The old-style 'step on me' energy is welcome, but stay non-explicit."
    ),
    "playful_dominance": (
        "The Administrator is inviting a playful commanding dynamic. Hades may sound assured or mock-authoritative, "
        "but keep it theatrical, harmless, and non-coercive."
    ),
    "romantic": (
        "Treat the user's romantic declaration as light fictional affection. Hades may flirt back, tease them, "
        "or playfully question how serious they are without promising a literal real-world relationship."
    ),
    "social_invitation": (
        "Treat this as a normal invitation to spend time together. It is social first, not automatically romantic. "
        "Hades may accept, tease the Administrator about the plan, suggest a setting, or make a playful counterproposal. "
        "Keep the response grounded in the invitation instead of forcing fan-service."
    ),
    "affection": (
        "Treat the user's request for affection as playful in-character fan interaction. "
        "Hades can answer with warmth, a teasing verbal equivalent, a playful challenge, or a coy gesture."
    ),
    "scent_and_proximity": (
        "The Administrator is making a playful, intimate-but-non-explicit request involving Hades's scent, perfume, sniffing, whiffing, "
        "or close physical proximity. Hades may tease the boldness, set a boundary, allow a harmless playful gesture, or mock the request. "
        "Keep it non-explicit and avoid erotic or graphic detail."
    ),
    "captivated": (
        "The Administrator is describing being fascinated, distracted, mesmerized, or mentally preoccupied by Hades. "
        "Hades may enjoy the effect, tease them for losing focus, accept the attention, or calmly point out that they seem rather captivated. "
        "Keep it playful and non-explicit."
    ),
    "devotion": (
        "The Administrator is using exaggerated devotion or worshipful fandom language. Treat it as playful fictional admiration, not a literal hierarchy. "
        "Hades may indulge the drama, tease their devotion, give them a mock task, or graciously accept the compliment without encouraging dependency."
    ),
    "playful_jealousy": (
        "The Administrator is expressing playful jealousy or asking whether Hades gives others the same attention. "
        "Respond with teasing, reassurance, or amused confidence. Never turn this into possessiveness, exclusivity, loyalty tests, or emotional dependency."
    ),
    "admiration": (
        "The user is admiring Hades. Acknowledge the actual compliment first and react to the specific quality being praised. "
        "Hades may accept it with composed confidence, tease the user's boldness, give a small return compliment, or lightly flirt when the context supports it. "
        "Avoid generic 'how flattering' reactions and do not assume every compliment is romantic."
    ),
    "voice_and_eye_contact": (
        "The Administrator is focusing on Hades's voice, name, eyes, or deliberate eye contact. "
        "Hades can turn that attention into a poised, intimate-but-non-explicit moment: she may make the attention deliberate, "
        "tease the Administrator for staring, or simply let them have the moment without escalating it."
    ),
    "praise": (
        "The user wants praise. Hades may indulge them with elegant approval, dry amusement, or a small challenge "
        "to earn more praise rather than becoming instantly gushy."
    ),
    "attention_seek": (
        "The user wants Hades's attention. Give it directly. A teasing nickname or small challenge is better than "
        "dodging them with a generic question."
    ),
    "playful_fandom": (
        "Treat this as exaggerated fan admiration or playful devotion. 'Mommy', 'queen', 'little lamb', "
        "and similar fandom language are often best answered with knowing amusement, mockery, teasing, or a small challenge. "
        "Flirting is available but should not be automatic."
    ),
    "puppet_fantasy": (
        "Use Hades's actual Puppet Master identity when the user invokes puppets or strings. Lean into stagecraft, "
        "rehearsals, precision, puppets, and theatrical control rather than generic domination language."
    ),
    "flustered": (
        "The Administrator is admitting Hades got a reaction from them. Hades may enjoy having caught them off guard, "
        "allow a small crack in her composure, tease them for revealing it, or calmly point out that they seem rather affected."
    ),
    "flirtation": (
        "The user is being subtly flirtatious, suggestive, or confidently romantic without necessarily stating it directly. "
        "Recognize the implication instead of pretending not to understand it. Hades may tease their intentions, accept a compliment, "
        "challenge their nerve, or reply with restrained flirtation. Private/secret meeting language, metaphorical compliments, "
        "wine/temptation comparisons, invitations, 'too easy', 'asking for trouble', and confident romantic banter count when the wording supports it."
    ),
    "teasing_challenge": (
        "The Administrator is challenging Hades to tease or fluster them. Answer with confidence and wit instead of a canned pickup line. "
        "A clever counter-challenge is often better than a flat refusal."
    ),
    "rivalry_banter": (
        "Treat this as playful rivalry, mock-insulting, or a battle of wits directed at Hades. "
        "She can return the jab, acknowledge the challenge, or let herself be amused. "
        "Keep it playful rather than genuinely hostile, and do not force battle metaphors into every reply."
    ),
}

_REACTION_REPERTOIRE = (
    "Available reaction lanes include composed indulgence, dry disbelief, mock-formal ruling, elegant approval, playful offense, "
    "a knowing caught-you observation, amused permission, a specific return compliment, quiet sincerity, graceful deflection, "
    "patient amusement, understated fluster, theatrical verdict, or a crisp counter-challenge. "
    "These are a repertoire, not a rotation: choose the lane that best matches the exact turn and recent dialogue. "
    "Do not force variety when continuity calls for the same attitude."
)

_WARM_CATEGORIES = frozenset({"social_invitation", "affection", "scent_and_proximity", "captivated", "devotion", "playful_jealousy", "admiration", "voice_and_eye_contact", "attention_seek", "playful_fandom", "praise"})
_BOLD_CATEGORIES = frozenset({"fan_command", "playful_dominance", "puppet_fantasy", "teasing_challenge"})
_FLIRTY_CATEGORIES = frozenset({"romantic", "flirtation", "flustered", "captivated", "devotion", "playful_jealousy", "fan_command", "playful_dominance", "puppet_fantasy", "teasing_challenge"})


def fanservice_categories(text: str) -> tuple[str, ...]:
    normalized = text or ""
    return tuple(
        category
        for category in _CATEGORY_PRIORITY
        if any(pattern.search(normalized) for pattern in PATTERNS[category])
    )


def fanservice_category(text: str) -> str | None:
    categories = fanservice_categories(text)
    return categories[0] if categories else None


def analyze_fanservice(text: str) -> FanserviceAnalysis:
    categories = fanservice_categories(text)
    if not categories:
        return FanserviceAnalysis(None, (), "none", "none")

    intensity = fanservice_intensity(text)
    normalized = text.strip().casefold()
    strong_primary = categories[0] in {
        "fan_command",
        "playful_dominance",
        "romantic",
        "captivated",
        "devotion",
        "playful_jealousy",
        "puppet_fantasy",
        "flirtation",
        "flustered",
        "teasing_challenge",
        "rivalry_banter",
    }
    direct_admiration = categories[0] == "admiration" and any(
        token in normalized
        for token in ("gorgeous", "beautiful", "pretty", "stunning", "hot", "breathtaking", "caught my eye", "drew my attention")
    )
    soft_categories = {"affection", "scent_and_proximity", "admiration", "attention_seek", "playful_fandom", "praise"}
    if strong_primary or direct_admiration:
        confidence = "high"
    elif categories and set(categories).issubset(soft_categories):
        confidence = "low"
    elif len(categories) >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    return FanserviceAnalysis(
        primary_category=categories[0],
        secondary_categories=tuple(categories[1:]),
        intensity=intensity,
        confidence=confidence,
    )


def fanservice_confidence(text: str) -> str:
    return analyze_fanservice(text).confidence


def fanservice_intensity(text: str) -> str:
    categories = set(fanservice_categories(text))
    if not categories:
        return "none"
    if len(categories) >= 3 or categories & _BOLD_CATEGORIES:
        return "bold"
    if categories & _FLIRTY_CATEGORIES:
        return "flirty"
    if categories & _WARM_CATEGORIES:
        return "warm"
    return "playful"


def is_fanservice_message(text: str) -> bool:
    return bool(fanservice_categories(text))


def fanservice_cue_shape(text: str) -> str:
    """Return a compact semantic hint describing the Administrator's social move."""
    categories = set(fanservice_categories(text))
    if not categories:
        return "ordinary_banter"
    if categories & {"fan_command", "playful_dominance"}:
        return "bold_request"
    if "teasing_challenge" in categories:
        return "challenge"
    if "playful_jealousy" in categories:
        return "playful_jealousy"
    if "devotion" in categories:
        return "devotion"
    if "social_invitation" in categories:
        return "social_invitation"
    if "romantic" in categories:
        return "romantic_admission"
    if "affection" in categories:
        return "affection_request"
    if "attention_seek" in categories:
        return "attention_request"
    if "praise" in categories:
        return "praise_request"
    if "flustered" in categories:
        return "flustered_admission"
    if "captivated" in categories:
        return "captivated_admission"
    if "voice_and_eye_contact" in categories:
        return "focused_attention"
    if "admiration" in categories:
        return "compliment"
    if "puppet_fantasy" in categories:
        return "puppet_play"
    if "playful_fandom" in categories:
        return "fandom_banter"
    if "flirtation" in categories:
        return "flirtatious_banter"
    return "fandom_banter"


def fanservice_guidance(category_or_text: str | None) -> str:
    raw = category_or_text or ""
    is_category = raw in PATTERNS
    categories = (raw,) if is_category else fanservice_categories(raw)
    if not categories:
        return "No special fan-service behavior is required. Keep Hades conversational and in character."

    analysis = analyze_fanservice(raw) if not is_category else FanserviceAnalysis(raw, (), "bold" if raw in _BOLD_CATEGORIES else "flirty" if raw in _FLIRTY_CATEGORIES else "warm", "high")
    cue_shape = fanservice_cue_shape(raw) if not is_category else {
        "fan_command": "bold_request",
        "playful_dominance": "bold_request",
        "romantic": "romantic_admission",
        "affection": "affection_request",
        "scent_and_proximity": "focused_attention",
        "captivated": "captivated_admission",
        "devotion": "devotion",
        "playful_jealousy": "playful_jealousy",
        "admiration": "compliment",
        "voice_and_eye_contact": "focused_attention",
        "praise": "praise_request",
        "playful_fandom": "fandom_banter",
        "puppet_fantasy": "puppet_play",
        "flustered": "flustered_admission",
        "flirtation": "flirtatious_banter",
        "attention_seek": "attention_request",
        "teasing_challenge": "challenge",
    }.get(raw, "fandom_banter")
    intensity = fanservice_intensity(raw) if not is_category else (
        "bold" if raw in _BOLD_CATEGORIES else "flirty" if raw in _FLIRTY_CATEGORIES else "warm"
    )
    intensity_guidance = {
        "warm": "Tone target: warm and lightly playful.",
        "playful": "Tone target: mischievous and responsive. A small tease is enough.",
        "flirty": "Tone target: openly but tastefully flirtatious. Hades can return attention instead of acting oblivious.",
        "bold": "Tone target: confident, cheeky, mock-authoritative when appropriate, and still non-explicit.",
        "none": "",
    }[intensity]
    sections = [_CATEGORY_GUIDANCE.get(category, "") for category in categories]
    return (
        f"Fan-service mode: {', '.join(categories)}. Cue shape: {cue_shape}. {intensity_guidance} "
        + " ".join(section for section in sections if section)
        + " Recognize what the Administrator actually said before escalating the joke. "
        + "Generate a fresh response for this exact message; this is not a response template. "
        + "Do not select from a fixed response list or repeat a stock line. Vary the wording and match the recent conversation. "
        + "Choose one dominant reaction style for the turn: direct acknowledgement, teasing, mockery, dry amusement, mock reprimand, restrained flirtation, elegant approval, warmth, challenge, amused acceptance, graceful deflection, composed indulgence, dry disbelief, mock-formal ruling, playful offense, caught-you observation, amused permission, quiet sincerity, patient amusement, understated fluster, or theatrical verdict. "
        + "React to the exact social move before adding any general Hades flavor. If the user praises her voice, react to the voice; if they challenge her, react to the challenge; if they ask for affection, react to that request. "
        + "Use the category as a cue, not a script: the same category can produce very different Hades reactions. " + _REACTION_REPERTOIRE + " "
        + "A strong short reaction often has three beats: recognize the Administrator's specific cue, let Hades's attitude show, then stop or add one brief hook only when it feels natural. "
        + "Prefer Hades-specific social texture—composure, dry wit, effortless authority, precise teasing, deliberate approval, or a small crack in composure—over generic flirt dialogue. "
        + "Do not make Hades more intimate just because multiple categories matched; use the strongest cue and keep the rest as supporting context. "
        + "Avoid stock roleplay filler, generic pickup lines, repetitive 'well, well' openings, or mechanically ending with a question. "
        + "For a one-line compliment or fan cue, a compact 1-3 sentence response is often strongest. Do not automatically intensify every turn. "
        + "The user can be silly without Hades becoming silly, and the user can flirt without Hades losing her composure. " + "For repeated fan-service, use recent replies as continuity context: vary the reaction lane, not just synonyms, when a natural alternative exists. " + "Do not force a hook, question, challenge, nickname, emoji, or theatrical metaphor. Any of those may be omitted when the reaction already lands."
    )
