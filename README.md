<h1>Cafeshop</h3>
<h2>main URIs</h2>
<ul>
  <li>/ | главная страница, список заказов</li> 
  <li>/create | страница формления заказа</li>
  <li>/[order_id]/edit | страница смены статуса заказа</li>
  <li>/[order_id]/delete | страница удаления заказа</li>
  <li>/paid | страница выручки</li>
</ul>
<h2>REST API</h2>
<ul>
  <li>GET /api/v1/orders | Отображение списка заказов</li>
  <li>POST /api/v1/orders | Создание нового заказа</li>
  <li>PUT /api/v1/orders/[order_id] | смена статуса заказа</li>
  <li>DELETE /api/v1/orders/[order_id] | удаление заказа</li>
  <li>PUT /api/v1/orders/revenue | Получение данных об общей выручке</li>
</ul>
<h2>Тесты</h2>
Находятся в директории ./cafeshop/orders/tests
<h2>Стек</h2>
<ul>
  <li>Django 5.1.5</li>
  <li>Python 3.11.9</li>
  <li>HTML/CSS</li>
  <li>PostgreSQL</li>
</ul>
