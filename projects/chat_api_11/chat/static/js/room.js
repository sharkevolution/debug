console.log("Sanity check from room.js.");

const roomName = JSON.parse(document.getElementById('roomName').textContent);
let echoUser = '';

let chatLog = document.querySelector("#chatLog");
let chatMessageInput = document.querySelector("#chatMessageInput");
let chatMessageSend = document.querySelector("#chatMessageSend");
let onlineUsersSelector = document.querySelector("#onlineUsersSelector");

let allUsersSelector = document.querySelector("#allUsersSelector");  // Список пользователей
let chatUserSelectorAdd = document.querySelector("#userAddRoom");
let chatUserSelectorRemove = document.querySelector("#userRemoveRoom");
let chatScroll = document.querySelector("#chatScroll");

let messageList = document.querySelector('#messages');
let chatInsertLi = document.querySelector('#chatTest');

// adds a new option to 'onlineUsersSelector'
function onlineUsersSelectorAdd(value, status = 'offline') {

    if (document.querySelector("#onlineUsersSelector option[value='" + value + "']")) return;

    let newOption = document.createElement("option");
    newOption.value = value;
    if (status == 'offline') {
        newOption.setAttribute('class', "fa fa-circle-o");
    } else {
        newOption.setAttribute('class', "fa fa-check-square");
        newOption.style.color = "green";
    }
    newOption.innerHTML = '&nbsp' + value;
    onlineUsersSelector.appendChild(newOption);
}

// removes an option from 'onlineUsersSelector'
function onlineUsersSelectorRemove(value) {
    let oldOption = document.querySelector("#onlineUsersSelector option[value='" + value + "']");
    if (oldOption !== null) oldOption.remove();
}

// update status user to offline 'offlineUsersSelectorChangeStatus'
function offlineUsersSelectorChangeStatus(value) {
    let statusOption = document.querySelector("#onlineUsersSelector option[value='" + value + "']");
    statusOption.setAttribute('class', "fa fa-circle-o");
    statusOption.style.color = "grey";
}

// update status user to online 'onlineUsersSelectorChangeStatus'
function onlineUsersSelectorChangeStatus(value) {
    let statusOption = document.querySelector("#onlineUsersSelector option[value='" + value + "']");
    statusOption.setAttribute('class', "fa fa-check-square");
    statusOption.style.color = "green";
}

// Добавление списка всех пользователей, adds a new option to 'allUsersSelector' 
function allUsersSelectorAdd(value) {
    for (const element of value) {
        if (document.querySelector("#allUsersSelector option[value='" + element + "']")) return;
        let newOption = document.createElement("option");
        newOption.value = element;
        newOption.innerHTML = element;
        allUsersSelector.appendChild(newOption);
    }
}

// focus 'chatMessageInput' when user opens the page
chatMessageInput.focus();

// submit if the user presses the enter key
chatMessageInput.onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter key
        chatMessageSend.click();
    }
};

// clear the 'chatMessageInput' and forward the message
chatMessageSend.onclick = function () {
    if (chatMessageInput.value.length === 0) return;
    // Отправка сообщения
    chatSocket.send(JSON.stringify({
        "message": chatMessageInput.value,
    }));
    chatMessageInput.value = "";
};

// focus 'userAddRoom' when user opens the page
chatUserSelectorAdd.focus();

// Пользователи на добавление в группу 
chatUserSelectorAdd.onclick = function () {
    // console.log('Add new users to the room');
    var selected = [];
    for (var option of document.getElementById('allUsersSelector').options) {
        if (option.selected) {
            selected.push(option.value);
        }
    }
    chatSocket.send(JSON.stringify({
        "participantes": { 'userAddRoom': selected },
    }));
};

// focus 'userRemoveRoom' when user opens the page
chatUserSelectorRemove.focus();

// Пользователи на удаление из группы 
chatUserSelectorRemove.onclick = function () {
    console.log('Delete users into to the room');
    var selected = [];
    for (var option of document.getElementById('allUsersSelector').options) {
        if (option.selected) {
            selected.push(option.value);
        }
    }
    chatSocket.send(JSON.stringify({
        "participantes": { 'userRemoveRoom': selected },
    }));
};

// Send echo username
function chatEchoSend() {
    chatSocket.send(JSON.stringify({
        "echo": 'username',
    }));
};

function chat_open_page_history() {
    chatSocket.send(JSON.stringify({
        "messages_history": {'navigation_open_page': 1},
    }));
};

// Scroll textArea
chatScroll.onclick = function () {
    messageList.scrollTop = messageList.scrollHeight;
};

// Update base, status messages is_read
const update_messages_is_read = async(ws) =>{
    if (super_box_is_read.length > 0) {
        chatSocket.send(JSON.stringify({
            "messages_is_read": super_box_is_read,
        }));
    }
}

let chatSocket = null;

function connect() {
    chatSocket = new WebSocket("ws://" + window.location.host + "/ws/chat/" + roomName + "/");

    chatSocket.onopen = function (e) {
        console.log("Successfully connected to the WebSocket.");
        
        chatEchoSend();
        chat_open_page_history();

        console.log("Start History");
        // Send update messages delivered status, time interval every 4sec 
        let interval = setInterval(()=> update_messages_is_read(chatSocket), 4000);
    }

    chatSocket.onclose = function (e) {
        console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 2s...");
        setTimeout(function () {
            console.log("Reconnecting...");
            connect();
        }, 2000);
    };

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        switch (data.type) {
            case "chat_message":
                // chatLog.value += data.user + ": " + data.message + "\n";
                // user_view = data.user;
                drawMessage(data, data.user);
                break;
            case "user_list":
                // participantes list and status
                console.log('user_list');
                clear_onlineUsersSelectorAdd();
                for (const key of Object.keys(data.participantes)) {
                    // console.log(key + ":" + data.participantes[key]);
                    onlineUsersSelectorAdd(key, data.participantes[key]);
                };
                break;
            case "user_join":
                // Присоединение пользователя в комнату
                // chatLog.value += data.user + " joined the room.\n";
                allUsersSelectorAdd(data.contacts);
                break;
            case "user_leave":
                // chatLog.value += data.user + " left the room.\n";
                // onlineUsersSelectorRemove(data.user);

                clear_onlineUsersSelectorAdd();
                for (const key of Object.keys(data.participantes)) {
                    console.log(key + ":" + data.participantes[key]);
                    onlineUsersSelectorAdd(key, data.participantes[key]);
                };
                break;
            case "private_message":
                chatLog_value = "PM from " + data.user + ": " + data.message + "\n";
                drawMessage(data, data.user, chatLog_value, 'New!');
                break;
            case "private_message_delivered":
                chatLog_value = "PM to " + data.target + ": " + data.message + "\n";
                drawMessage(data, echoUser, chatLog_value, '');
                messageList.scrollTop = messageList.scrollHeight;
                break;
            case "private_quit":
                // Пользователя удалили, выход из комнаты
                if (data.room == roomName) { window.location.pathname = "chat/" };
                break;
            case "user_update":
                // Обновляем участников комнаты после изменений
                clear_onlineUsersSelectorAdd();

                for (const key of Object.keys(data.participantes)) {
                    console.log(key + ":" + data.participantes[key]);
                    onlineUsersSelectorAdd(key, data.participantes[key]);
                };
                break;
            case "user_echo":
                echoUser = data.user;
                break;
            
            case "update_messages_is_read":
                
                for (const key of Object.keys(data.messages_is_read)) {

                    // console.log(data.messages_is_read[key]);
                    var ms = data.messages_is_read[key]
                    if (ms[0] == true){
                        var up_status = "bi bi-check-all";
                    }else{
                        var up_status = "bi bi-check";

                    }
                    let box = document.getElementById(key);
                    let child = box.children;
                    let child_is_read = child[1].children[0].children[1];
                    let child_datetime = child[1].children[0].children[2];
                    let child_new_text = child[1].children[0].children[3];

                    let child_avatar = child[0];
                    let avatar = child_avatar.textContent;
                    if (avatar == echoUser){
                        child_is_read.setAttribute("class", up_status);
                        child_datetime.innerHTML = `<p>${ms[1]}</p>`;
                    }
                    if (ms[0] == true){child_new_text.innerHTML = `<p></p>`;}
                    // Update unread messages
                    chatScroll.textContent = data.messages_unread.length;

                };
                break;
            case "history_navigation":
                // console.log("history_navigation");
                wrap_history(data);
                
                if (data.direction == 'open'){
                    messageList.scrollTop = 0;
                }

                break;

            default:
                console.error("Unknown message type! " + data.type);
                break;
        }
    };

    chatSocket.onerror = function (err) {
        console.log("WebSocket encountered an error: " + err.message);
        console.log("Closing the socket.");
        chatSocket.close();
    }
}
// ****************
connect();
// ****************

onlineUsersSelector.onchange = function () {
    chatMessageInput.value = "/pm " + onlineUsersSelector.value + " ";
    onlineUsersSelector.value = null;
    chatMessageInput.focus();
};

// Clear onlineUsersSelectorAdd
function clear_onlineUsersSelectorAdd() {
    var select = document.getElementById("onlineUsersSelector"),
        length = select.options.length;
    while (length--) {
        select.remove(length);
    }
}


function wrap_history(data){
    for (const key of data.update_navigation) {
        history_data = key

        if (history_data.is_read == true){
            var up_status = "bi bi-check-all"
        }else{
            var up_status = "bi bi-check"
        }
        var new_message = '';

        // Add message to chat
        let position = 'left'; 
        if (history_data.user == echoUser) {position = 'right';}

        if ( !(history_data.user ==  history_data.recipient) && history_data.user == echoUser ){
            //private_delivered 
            chatLog_value = "PM to " + history_data.recipient + ": " + history_data.content + "\n";
            user_view = echoUser;
        }else if
            ( !(history_data.user == history_data.recipient) && history_data.recipient == echoUser) {
            //private_message from
            chatLog_value = "PM from " + history_data.user + ": " + history_data.content + "\n";
            user_view = history_data.user;
            var up_status = "bi bi-check"
            if (history_data.is_read == false){ var new_message = 'New!';}            
        } else if 
            (history_data.recipient == history_data.user && history_data.recipient == echoUser) {
            //public message from
            chatLog_value = history_data.content + "\n";
            user_view = history_data.user;
        } else {
            //public message to
            chatLog_value = history_data.content + "\n";
            user_view = history_data.user;
            // console.log(!(history_data.user == history_data.recipient));
            // console.log(history_data.recipient == echoUser);
            // console.log( !(history_data.user == history_data.recipient) && history_data.recipient == echoUser);
        }

        box_exists = document.getElementById(`box-${history_data.id}`);
        if (!box_exists) {
            const messageItem = `
                    <li class="message ${position} box" id="box-${history_data.id}">
                        <div class="avatar">${user_view}</div>
                            <div class="text_wrapper">
                                <div class="text"> ${chatLog_value}<br>
                                <div id="is_read" class="${up_status}"></div>
                                <div id="is_created"><p>${history_data.created}</p></div>
                                <div id="is_new"><p>${new_message}</p></div>
                            </div>
                        </div>
                    </li>`;

            var ulbox = document.getElementById("messages");

            if (data.direction == 'back'){
                if (ulbox.getElementsByTagName("li").length > 0) {
                    let li0 = ulbox.children[0];
                    li0.insertAdjacentHTML("beforeBegin", messageItem);
                }
                else{
                    ulbox.innerHTML += messageItem;
                }
            }
            if (data.direction == 'forward' | data.direction == 'open'){
                    ulbox.innerHTML += messageItem;
            }           
            // // Callback Observer API Intersection
            const boxes = document.querySelectorAll('.box');
            boxes.forEach(element => observer.observe(element));
        }
    };
}

function drawMessage(data, user_view='', chatlog_value='', new_message='') {
    // Add message to chat
    let position = 'left'; 
    if (user_view == echoUser) {
        position = 'right';
    }

    if (chatlog_value) {
        var sms = chatlog_value
    }else{
        var sms = data.message
    }

    if (data.message_is_read == true){
        var up_status = "bi bi-check-all"
    }else{
        var up_status = "bi bi-check"
    }

    let box = "";
    let created = "";
    if (data.message_id > 0) {
        box = `box-${data.message_id}`
        created = data.message_created
    }
    console.log(data.message_id);
    const messageItem = `
            <li class="message ${position} box" id="${box}">
                <div class="avatar">${user_view}</div>
                    <div class="text_wrapper">
                        <div class="text">${sms}<br>
                        <div id="is_read" class="${up_status}"></div>
                        <div id="is_created"><p>${created}</p></div>
                        <div id="is_new"><p>${new_message}</p></div>
                    </div>
                </div>
            </li>`;
    messageList.innerHTML += messageItem;

    // Callback Observer API Intersection
    const boxes = document.querySelectorAll('.box');
    boxes.forEach(element => observer.observe(element));
}

// Set up the throttler 
// Функция throttle будет принимать 2 аргумента:
// - callee, функция, которую надо вызывать;
// - timeout, интервал в мс, с которым следует пропускать вызовы.
function throttle(callee, timeout) {
    // Таймер будет определять,
    // надо ли нам пропускать текущий вызов.
    let timer = null
  
    // Как результат возвращаем другую функцию.
    // Это нужно, чтобы мы могли не менять другие части кода,
    // чуть позже мы увидим, как это помогает.
    return function perform(...args) {
      // Если таймер есть, то функция уже была вызвана,
      // и значит новый вызов следует пропустить.
      if (timer) return
  
      // Если таймера нет, значит мы можем вызвать функцию:
      timer = setTimeout(() => {
        // Аргументы передаём неизменными в функцию-аргумент:
        callee(...args)
  
        // По окончании очищаем таймер:
        clearTimeout(timer)
        timer = null
      }, timeout)
    }
  }
  
// handle event WHELL UP mouse in the chat
function wheel_up (event) {
    
    const boxes = document.querySelectorAll('.box');
    boxes.forEach(element => observer.observe(element));

    if (event.deltaY < 0) {
        // console.log(super_box_is_read);
        // Отправка запроса на обновление
        chatSocket.send(JSON.stringify({
            "messages_history": {'navigation_back': super_box_is_read},
        }));
        console.log('scrolling wheel up: ' + super_box_is_read);
    }else{
        chatSocket.send(JSON.stringify({
            "messages_history": {'navigation_forward': super_box_is_read},
        }));
        console.log('scrolling wheel down: ' + super_box_is_read);
    }
}
messageList.addEventListener('wheel', throttle(wheel_up, 50)); 


const debug = document.querySelector('.debug');
const displayed = {};

const observer = new IntersectionObserver(scrollTracking, {
    threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
});

let super_box_is_read = [];  // Список для хранения множества сообщений is_read

function scrollTracking(entries) {
    for (const entry of entries) {
        displayed[entry.target.id] = entry.intersectionRatio >= 0.2;
    }
    debug.textContent = Object
        .entries(displayed)
        .filter(([id, inViewport]) => inViewport)
        .map(([id, inViewport]) => id)
        .join('\n');
    
    let i = 0;
    let box_status = [];
    for (const key of Object.keys(displayed)) {      
        if (key.length > 0) {
            if (displayed[key]) {
                box_status[i] = key;
                i += 1; 
            }
        }
    }
    if (box_status.length > 0) {
        super_box_is_read = box_status;
    }
    console.log("ScrollTracking: " + super_box_is_read);
}
  
