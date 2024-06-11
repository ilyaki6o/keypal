## Начальная клавиатура
    --------------------------------------------
    |                   <GET>                  |
    --------------------------------------------
    |       <SET>         |       <UPDATE>     |
    --------------------------------------------

### Кнопка `<GET>`
Предназначение: получить пароль, ассоциированный с парой `<URL>, <LOGIN>`.

При клике на `<GET>` бот просит ввести сайт, на котором требуется ввести пароль, путем вывода
сообщения "Введите сайт для поиска".
Сайт можно вводить как часть URL (например "goo" для "www.google.com").

Если введенная часть встречается в нескольких записях с сайтами, вывести все варианты как `inline_keyboard` в ответном
сообщении. Если вариантов будет больше 5, разбить `inline_keyboard` на страницы и вывести в конце списка кнопки `<PREV>` и `<NEXT>`
для навигации по страницам. Перелистывание страниц осуществляется путём
редактирования сообщения и вывода новых кнопок.
Варианты отсортированы в алфавитном порядке (в будущем можно добавить сортировку по
частоте обращения). Если введенная часть соответствует только одному сайту, то сообщение
с выбором не выводится, отправляется только подтверждение выбора "выбран сайт `<SITE>`".
Если подходящего сайта нет, вывести сообщение об этом: "нет записей для данного сайта".

После выбора сайта аналогичная логика применяется для выбора логина на этом сайте, с тем
отличием, что рассматривается полный список логинов, зарегестрированных в системе для
этого сайта. Далее выдаётся пароль, соответствующий паре `<URL>, <LOGIN>`.

Для быстрого копирования окружить пароль тремя обратными апострофами \`\`\``<password`\`\`\`.
При отправке сообщения использовать тип разметки `MarkdownV2`

> **_TODO:_** Подумать над быстрым форматом ввода. Например `<PART_URL>, <PART_LOGIN>`, чтобы
пользователь вводил одним сообщением сразу всю информацию о необходимом пароле.

По прошествии тайм-аута (задаётся в настройках) бот удаляет все сообщения (свои и пользователя), начиная с
выбора сайта и заканчивая отправкой пароля.

### Кнопка `<SET>`
Предназначение: установить пароль, соответствующий паре `<URL>, <LOGIN>`.

Бот просит ввести сначала `<URL>`, отправляя сообщение "Введите адрес сайта, для которого сохранять пароль".
Далее `<LOGIN>`: "Введите логин на этом сайте, для которого сохранять пароль".

Если пользователь ввел полный `<URL>`, оставить только "базовую часть", например,
"www.google.com". Если пара `<URL>, <LOGIN>` уже зарегестрирована в системе,
спросить пользователя, нужно ли обновлять пароль. Для этого отправить сообщение:
"Пароль для такого адреса и логина уже существует. Вы хотите заменить его?" вместе
с `inline_keyboard` с вариантами ответа `     ДА      |    НЕТ    `. После нажатия пользователем
на кнопку, бот редактирует данное сообщение и выводит вместо него подтверждение действия:
"Пароль успешно обновлён" или "Добавление пароля отменено".

Далее бот просит ввести пароль: "Введите пароль для `<URL, <LOGIN>`" и сохраняет его в системе
для дальнейшего использования.

> **_TODO:_** Подумать над функциями проверки надёжности пароля и автогенерации пароля.

По прошествии тайм-аута (задаётся в настройках) бот удаляет все сообщения (свои и пользователя), начиная с
ввода сайта и заканчивая отправкой пароля.

### Кнопка `<UPDATE>`
Предназначение: обновить пароль, ассоциированный с парой `<URL, <LOGIN>`.

Логика работы практически совпадает с логикой кнопки `<GET>`.

## Команды
/settings
: переход в режим настроек. В этом режиме можно настраивать тайм-аут для удаления сообщений
и ещё что-нибудь, я пока не придумал.

## Дополнительные команды
> **_TODO_**: возможна реализация дополнительных команд:
> - /backup - создание бэкапа всех сохранённых паролей.
> - /import - импорт паролей из файла.
