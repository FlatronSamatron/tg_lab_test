**ТЕСТОВЕ ЗАВДАННЯ**

Зробити невеликий backend-сервіс для керування експедиціями.

***У системі є:***  
\- керівник експедиції (**chief**),  
\- учасники (**member**),  
\- життєвий цикл експедиції,  
\- події в реальному часі (WebSocket),

***Умови:*** 

- Стек вільний (Django, FastAPI, Flask)  
- Формат авторизації на вибір (JWT/session)  
- UI не потрібен   
- Потрібен лише backend \+ README  
- Буде плюсом написання тестів та збірка в Docker

**Моделі бази даних**  
***User:***  
\- id  
\- email (unique)  
\- name  
\- role (chief | member)  
\- created\_at  
\- updated\_at

***Expedition***  
\- id  
\- title  
\- description (nullable)  
\- status (draft | ready | active | finished)  
\- start\_at (datetime)  
\- end\_at (nullable)  
\- capacity (int)  
\- chief\_id (FK \-\> User)  
\- created\_at  
\- updated\_at

***ExpeditionMember:***  
\- id  
\- expedition\_id (FK \-\> Expedition)  
\- user\_id (FK \-\> User)  
\- state (invited | confirmed |)  
\- invited\_at  
\- confirmed\_at (nullable)

**Переходи статусів Expedition**

***Дозволені лише такі переходи:***  
*\- \`draft \-\> ready\`*  
*\- \`ready \-\> active\`*  
*\- \`active \-\> finished\`*

**draft:**  
\- Статус встановлюється автоматично під час створення.  
\- На цьому етапі chief формує склад: запрошує учасників, учасники підтверджують участь.

**ready:**  
\- У цей статус переводить лише chief  
\- Перед переходом перевіряється, що експедиція ще не active/finished.

**active:**  
\- У цей статус переводить лише chief  
\- Перед стартом одночасно мають бути істинні всі умови:

* start\_at \<= now().  
* Кількість confirmed учасників \>= 2\.  
* Кількість confirmed учасників \<= capacity.  
* Жоден confirmed учасник не має перебувати в іншій active експедиції.

**finished:**  
\- Дозволено тільки з active.  
\- Після finished експедиція вважається завершеною: повторний start/set-ready заборонені.

***Правила запрошень***  
\- Запрошувати можна лише користувачів з роллю member.  
\- Не можна запрошувати одного й того самого учасника в ту саму експедицію повторно.  
\- Підтверджувати може лише сам запрошений користувач.  
\- Підтвердити можна лише стан invited \-\> confirmed.

**Websocket**

WS має в real-time віддавати події по експедиціях (member\_invited, member\_confirmed, expedition\_status) тільки авторизованим користувачам і лише для тих експедицій, де вони chief або учасники.