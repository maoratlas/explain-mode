<div dir="rtl">

# explain-mode

**מצב הוראה סבלני לסוכני קידוד מבוססי בינה מלאכותית — נבנה עבור ילדים ועבור דוברי שפות שנכתבות מימין לשמאל, כמו עברית וערבית, שלומדים לתכנת.**

[Read in English](README.md)

צ'אטים מבוססי טרמינל נותנים חוויה גרועה במיוחד לשתי הקבוצות האלה: הסברים
ארוכים קשים לקריאה נוחה לילד בחלון צ'אט שגולל, וטקסט בעברית או בערבית
לעיתים קרובות מוצג בצורה מבולגנת או מתערבב בצורה מבלבלת עם קוד ופקודות
באנגלית. `explain-mode` פותר את שתי הבעיות — תוך שהוא נשאר כללי מספיק כדי
לעזור לכל מתחיל.

עובד עם <span class="ltr" dir="ltr" style="unicode-bidi:isolate">Claude Code, Cursor, Codex</span>,
וכל סוכן קידוד מבוסס בינה מלאכותית שתומך ב"מיומנויות" (<span class="ltr" dir="ltr" style="unicode-bidi:isolate">skills</span>)
מבוססות <span class="ltr" dir="ltr" style="unicode-bidi:isolate">Markdown</span>.

## מה זה עושה

במקום לשפוך הסבר ארוך לתוך הצ'אט, `explain-mode` כותב כל שיעור לדף
<span class="ltr" dir="ltr" style="unicode-bidi:isolate">HTML</span>
עצמאי וקריא, ופותח אותו אוטומטית — בזמן שהצ'אט עצמו נשאר קצר ומשמש רק
לתשובות ולצעדים הבאים של הלומד.

## איך זה נראה בפועל

אותה שאלה — "תסביר לי מה זה API" — נשאלה בעברית, בלי ועם explain-mode:

<table dir="rtl">
<tr>
<th>עם explain-mode</th>
<th>בלי explain-mode</th>
</tr>
<tr>
<td><img src="docs/images/after-explain-mode.png" alt="אותו הסבר מוצג כדף רחב וקריא, עם תיבת הדגשה ושאלה שמזמינה את הלומד לחזור ולענות"></td>
<td><img src="docs/images/before-chat.png" alt="הסבר ארוך דחוס בפאנל הצ'אט הצר, גופן קטן, טקסט בעברית ובאנגלית מעורבב בכיוונים"></td>
</tr>
<tr>
<td>אותה בעיה בדיוק — עברית ואנגלית מעורבבות באותו משפט — נפתרת כאן: שימו לב
לדוגמה בדף ("מה מזג האוויר בתל אביב?"),
שבה הבקשה והתשובה מוצגות בתיבה נפרדת עם כיוון משלה, ולא בתוך משפט
עברי רציף. אותו הסבר כדף רחב וקריא: כותרות ברורות, דוגמה מבודדת, רעיון
מרכזי מודגש, מונחים באנגלית וקוד מבודדים בתיבות משלהם במקום לשבת בתוך
המשפט, ושאלה שמזמינה את הלומד לחזור לצ'אט — במקום רק לשפוך עליו מידע.</td>
<td>תשובה ארוכה דחוסה לתוך פאנל הצ'אט הצר — גופן קטן, בלי מרחב נשימה,
ושורות שבהן עברית עוטפת ישירות אנגלית באמצע המשפט, למשל:
"אתה שולח בקשה לכתובת בפורמט api.weather.com/tel-aviv ומקבל בחזרה נתוני מזג
אוויר כמו JSON" — קריא אם מתאמצים, אבל בדיוק הסוג של שורה מעורבת־כיוונים
שקורא צעיר או חדש נתקע עליה.</td>
</tr>
</table>

## למה כדאי להשתמש בזה

- **שיעורים קריאים, לא קיר של טקסט בצ'אט.** לכל הסבר יש דף משלו: גופן גדול,
  פסקאות קצרות, ריווח נדיב, רעיון אחד בכל פעם — במקום גלילה בטרמינל צפוף.
- **תמיכה אמיתית בכיווניות מימין לשמאל, לא תוספת בדיעבד.** עברית, ערבית,
  ושפות נוספות שנכתבות מימין לשמאל מוצגות עם כיוון וטקסט מיושר נכון, בעוד
  שקוד, פקודות ונתיבי קבצים נשארים מבודדים נכון משמאל לימין באותו דף — בלי
  יותר טקסט מעורבב שהופך לבלגן.
- **סגנון הוראה מותאם לילדים, כברירת מחדל.** משפטים קצרים, רעיון אחד בכל
  דף, דוגמה אחת, שאלה או משימה קטנה אחת — הסוכן מקבל הנחיה ללמד כמו מורה
  פרטי סבלני, לא לדהור קדימה כמו קבלן עצמאי.
- **הצ'אט נשאר שיחה, לא ספר לימוד.** תוכן ארוך לעולם לא מציף את היסטוריית
  הצ'אט; הצ'אט שמור לתשובות, שאלות ודו־שיח של הלומד.
- **הפרויקט של הלומד נשאר בטוח.** שיעורים מוצגים בדף נפרד וזמני משלהם,
  ולעולם לא בתוך קובצי הפרויקט האמיתיים של הלומד. שינויים בקבצי פרויקט
  אמיתיים מוסברים קודם, נשארים קטנים, ולעולם לא נכתבים מחדש בשקט עם פתרון
  מלא.
- **אפס שרת, אפס תלויות.** כל דף שיעור הוא קובץ
  <span class="ltr" dir="ltr" style="unicode-bidi:isolate">HTML</span>
  עצמאי אחד — בלי שלב בנייה, בלי שרת מקומי, בלי שום דבר להתקין מעבר
  למיומנות עצמה ו(אופציונלית) הגדרה חד־פעמית בעורך לתצוגה מקדימה בלי קליק.
- **עובד עם הסוכן שכבר יש לכם.** אין אפליקציה חדשה ללמוד — זהו קובץ
  <span class="ltr" dir="ltr" style="unicode-bidi:isolate">Markdown</span>
  שסוכן הקידוד הקיים שלכם קורא ופועל לפיו.
- **כללי מספיק כדי לגדול.** ילדים ודוברי שפות מימין לשמאל הם רק נקודת
  ההתחלה, לא הגבלה נוקשה — השפה, הכיוון, ופרופיל הלומד כולם ניתנים
  להגדרה, כך שזה מתאים גם למתחילים אחרים.

## התקנה

תנו לסוכן הקידוד שלכם את הכתובת של המאגר הזה, ובקשו ממנו להתקין את
המיומנות. לדוגמה, הדביקו את זה בתוך
<span class="ltr" dir="ltr" style="unicode-bidi:isolate">Claude Code, Cursor</span>,
או כלי דומה:

<pre dir="ltr" style="unicode-bidi:isolate; text-align:left;">
Please install the skill from https://github.com/maoratlas/explain-mode
into this project.
</pre>

סוכן מספיק יכולת יביא את הקובץ
<code class="ltr" dir="ltr" style="unicode-bidi:isolate">skills/explain-mode/SKILL.md</code>
מהמאגר הזה ויעתיק אותו למקום הנכון עבור הכלי שלכם באופן אוטומטי (עבור
<span class="ltr" dir="ltr" style="unicode-bidi:isolate">Claude Code</span>,
זה
<code class="ltr" dir="ltr" style="unicode-bidi:isolate">.claude/skills/explain-mode/SKILL.md</code>,
ברמת הפרויקט או המשתמש; <span class="ltr" dir="ltr" style="unicode-bidi:isolate">Cursor</span>
ו־<span class="ltr" dir="ltr" style="unicode-bidi:isolate">Codex</span>
קוראים גם את התיקייה הזאת, לצד תיקיות משלהם).

אפשרות נוספת: כלי ההתקנה הסטנדרטי
<a href="https://github.com/vercel-labs/skills"><span class="ltr" dir="ltr" style="unicode-bidi:isolate">skills CLI</span></a>,
שמזהה את מבנה המאגר הזה ומתקין לתיקייה הנכונה עבור כל סוכן שתשתמשו בו:

<pre dir="ltr" style="unicode-bidi:isolate; text-align:left;">
npx skills add maoratlas/explain-mode
</pre>

ואם הסוכן שלכם צריך הנחיה מפורשת יותר, השתמשו ב:

<pre dir="ltr" style="unicode-bidi:isolate; text-align:left;">
Fetch https://raw.githubusercontent.com/maoratlas/explain-mode/main/skills/explain-mode/SKILL.md
and save it as .claude/skills/explain-mode/SKILL.md in this project.
</pre>

בלי תלויות, בלי שלב בנייה, בלי שרת — זהו קובץ
<span class="ltr" dir="ltr" style="unicode-bidi:isolate">Markdown</span>
אחד.

### אופציונלי: תצוגה מקדימה של <span class="ltr" dir="ltr" style="unicode-bidi:isolate">HTML</span> בלי קליק

כברירת מחדל, פתיחת דף שיעור עשויה לדרוש קליק ידני אחד כדי לעבור מקוד
מקור גולמי לתצוגה מקדימה מוצגת, תלוי בעורך שלכם. קובץ המיומנות כולל
קטע **הגדרה חד־פעמית** קצר וניתן להעתקה
(<span class="ltr" dir="ltr" style="unicode-bidi:isolate">"One-time setup: click-free HTML preview"</span>)
שמסיר את הקליק הזה לגמרי עבור
<span class="ltr" dir="ltr" style="unicode-bidi:isolate">VS Code</span>
ועורכים מבוססי
<span class="ltr" dir="ltr" style="unicode-bidi:isolate">VS Code</span>
(<span class="ltr" dir="ltr" style="unicode-bidi:isolate">Cursor</span>
וכדומה). בקשו מהסוכן שלכם ללוות אתכם בתהליך, או פתחו את
<code class="ltr" dir="ltr" style="unicode-bidi:isolate">skills/explain-mode/SKILL.md</code>
ועקבו אחרי הקטע הזה בעצמכם.

## שימוש

אחרי ההתקנה, הפעילו את זה בכל שיחה עם הסוכן שלכם:

<pre dir="ltr" style="unicode-bidi:isolate; text-align:left;">
/explain-mode
</pre>

הסוכן יאשר שהמצב פעיל, ואז יתחיל לכתוב שיעורים לדף קריא בכל פעם שיש לו
משהו משמעותי להסביר — מושגי קוד, הוראות, תרגילים, או הסבר על שגיאה —
בזמן שהצ'אט עצמו נשאר קצר. אמרו "עצור מצב הסבר" (או ניסוח דומה) בכל שלב
כדי לכבות את זה.

## רישיון

[<span class="ltr" dir="ltr" style="unicode-bidi:isolate">MIT</span>](LICENSE)

</div>
