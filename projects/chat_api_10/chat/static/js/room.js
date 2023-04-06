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

// Scroll textArea
// chatScroll.onclick = function () {
//     chatLog.scrollTop = chatLog.scrollHeight;
// };

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
        // Send update messages delivered status, time interval every 3sec 
        let interval = setInterval(()=> update_messages_is_read(chatSocket), 3000);
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
                user_view = data.user;
                drawMessage(data, user_view);
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
                user_view = data.user;
                drawMessage(data, user_view, chatLog_value);
                break;
            case "private_message_delivered":
                chatLog_value = "PM to " + data.target + ": " + data.message + "\n";
                user_view = echoUser;
                drawMessage(data, user_view, chatLog_value);
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
                
                // console.log(data.messages_is_read);

                for (const key of Object.keys(data.messages_is_read)) {

                    // console.log(data.messages_is_read[key]);
                    if (data.messages_is_read[key] == true){
                        var up_status = "bi bi-check-all"
                    }else{
                        var up_status = "bi bi-check"
                    }
                    let box = document.getElementById(key);
                    let child = box.children;
                    let child_is_read = child[1].children[0].children[1];

                    let child_avatar = child[0];
                    let avatar = child_avatar.textContent;
                    if (avatar == echoUser){
                        child_is_read.setAttribute("class", up_status);                        
                    }

                };
                break;
            case "history_navigation":
                // Проверить и добавить истрорию, навигация по времени назад 
                // console.log('Place for add handler history_navigation');
                wrap_history(data);
                break;

            default:
                console.error("Unknown message type! " + data.type);
                break;
        }

        // var chatEm = convertEm(1.5);
        // scroll 'chatLog' to the bottom
        // if (chatLog.scrollHeight / chatEm >= 14) {
        //     chatScroll.textContent = 100;
        // };

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

// Converter Em and Rem
function getElementFontSize(context) {
    // Returns a number
    return parseFloat(
        // of the computed font-size, so in px
        getComputedStyle(
            // for the given context
            context ||
            // or the root <html> element
            document.documentElement
        ).fontSize
    );
}

// Convert Rem CSS to px
function convertRem(value) {
    return convertEm(value);
}

// Convert Em CSS to px 
function convertEm(value, context) {
    return value * getElementFontSize(context);
}

// Clear onlineUsersSelectorAdd
function clear_onlineUsersSelectorAdd() {
    var select = document.getElementById("onlineUsersSelector"),
        length = select.options.length;
    while (length--) {
        select.remove(length);
    }
}


function wrap_history(data){

    for (const key of data.update_navigation_back) {
        
        history_data = key
        // console.log('Key: ' + key);
        
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
            // console.log('I am too');
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

        // console.log(`box-${history_data}`);
        box_exists = document.getElementById(`box-${key.id}`);
        if (!box_exists) {

            const messageItem = `
                    <li class="message ${position} box" id="box-${history_data.id}">
                        <div class="avatar">${user_view}</div>
                            <div class="text_wrapper">
                                <div class="text"> ${chatLog_value}<br>
                                <div id="is_read"></div>
                                <div id="is_created"><p>${history_data.created}</p></div>
                            </div>
                        </div>
                    </li>`;

            let li0 = ul.children[0];
            li0.insertAdjacentHTML("beforeBegin", messageItem);

            // // Callback Observer API Intersection
            const boxes = document.querySelectorAll('.box');
            boxes.forEach(element => observer.observe(element));
        };

    };
}

function drawMessage(data, user_view='', chatlog_value='') {
    // Add message to chat
    let position = 'left'; 
    if (user_view === echoUser) {
        position = 'right';
    }

    if (chatlog_value) {
        var sms = chatlog_value
    }else{
        var sms = data.message
    }
    const messageItem = `
            <li class="message ${position} box" id="box-${data.message_id}">
                <div class="avatar">${user_view}</div>
                    <div class="text_wrapper">
                        <div class="text"> ${sms}<br>
                        <div id="is_read"></div>
                    </div>
                </div>
            </li>`;
    messageList.innerHTML += messageItem;

    // let change_status_html = document.getElementById("is_read");
    // change_status_html.setAttribute("class", "bi bi-check");

    // Callback Observer API Intersection
    const boxes = document.querySelectorAll('.box');
    boxes.forEach(element => observer.observe(element));
}

chatInsertLi.onclick = function () {
    let li0 = ul.children[0];
    li0.insertAdjacentHTML("beforeBegin", "<li>3</li><li>4</li>");
}

// const scroller = document.querySelector("#scroller");
const output = document.querySelector("#output");
var ul = document.getElementById("messages");
var nextItem = 1;

// Add New messages bottom chat 
var loadMore = function () {

    // Отправка запроса на обновление
    chatSocket.send(JSON.stringify({
        "messages_history": {'navigation_forward': super_box_is_read},
    }));

    console.log('scrolling down');
    for (var i = 0; i < 5; i++) {
        var item = document.createElement('li');
        item.innerText = 'Item ' + nextItem++;
        messageList.appendChild(item);
    }
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
    if (event.deltaY < 0) {

    // Отправка запроса на обновление
    chatSocket.send(JSON.stringify({
        "messages_history": {'navigation_back': super_box_is_read},
    }));

        // var ul = document.getElementById("messages");
        // var li0 = ul.children[0];
        // if (li0) {
        //     li0.insertAdjacentHTML("beforeBegin", "<li>3</li><li>4</li>");
        // };
        console.log('scrolling up');
    }
}
messageList.addEventListener('wheel', throttle(wheel_up, 100)); 

// handle event Scroll Chat
function scrolling_chat(event) {
    output.textContent = `scrollTop: ${messageList.scrollTop}`;
    if (messageList.scrollTop + messageList.clientHeight >= messageList.scrollHeight) {
        loadMore();
    }
    // Callback Observer API Intersection
    const boxes = document.querySelectorAll('.box');
    boxes.forEach(element => observer.observe(element));
}
messageList.addEventListener('scroll', throttle(scrolling_chat, 100)); 


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
        
        if (displayed[key]) {
            box_status[i] = key;
            i += 1; 
        };
    }

    // const set1 = new Set(box_status);
    // const set2 = new Set(super_box_is_read);
    // let different_set = getDifference(set1, set2);
    // let dif = Array.from(different_set);
    
    // super_box_is_read = super_box_is_read.concat(dif);
    super_box_is_read = box_status;
    // console.log('super_box_is_read: ' + super_box_is_read);

    // if (dif.length > 0) {
    //     // Update base, status messages is_read
    //     chatSocket.send(JSON.stringify({
    //         "messages_is_read": dif,
    //     }));
        // console.log('different set is read: ' + dif);
    // }
}

// get difference sets for status messages 'is_read'
// function getDifference(setA, setB) {
//     return new Set(
//       [...setA].filter(element => !setB.has(element))
//     );
//   }
  
