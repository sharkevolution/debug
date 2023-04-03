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

let chatSocket = null;

function connect() {
    chatSocket = new WebSocket("ws://" + window.location.host + "/ws/chat/" + roomName + "/");

    chatSocket.onopen = function (e) {
        console.log("Successfully connected to the WebSocket.");
        chatEchoSend();
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
                drawMessage(data);
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
                chatLog.value += data.user + " left the room.\n";
                // onlineUsersSelectorRemove(data.user);

                clear_onlineUsersSelectorAdd();
                for (const key of Object.keys(data.participantes)) {
                    console.log(key + ":" + data.participantes[key]);
                    onlineUsersSelectorAdd(key, data.participantes[key]);
                };
                break;
            case "private_message":
                chatLog.value += "PM from " + data.user + ": " + data.message + "\n";
                break;
            case "private_message_delivered":
                chatLog.value += "PM to " + data.target + ": " + data.message + "\n";
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
            default:
                console.error("Unknown message type!");
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

// Scroll textArea
chatScroll.onclick = function () {
    chatLog.scrollTop = chatLog.scrollHeight;
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

let box_iter = 0

function drawMessage(data) {
    let position = 'left';
    if (data.user === echoUser) position = 'right';
    box_iter += 1
    const messageItem = `
            <li class="message ${position} box" id="box-${box_iter}">
                <div class="avatar">${data.user}</div>
                    <div class="text_wrapper">
                        <div class="text">${data.message}<br>
                    </div>
                </div>
            </li>`;
    messageList.innerHTML += messageItem;
}

// Send echo username
function chatEchoSend() {
    chatSocket.send(JSON.stringify({
        "echo": 'username',
    }));
};

chatInsertLi.onclick = function () {
    // Добавляем элементы в начало
    var ul = document.getElementById("messages");
    var li5 = ul.children[0];

    li5.insertAdjacentHTML("beforeBegin", "<li>3</li><li>4</li>");

}

// const scroller = document.querySelector("#scroller");
const output = document.querySelector("#output");
var ul = document.getElementById("messages");
var nextItem = 1;

// Add New messages bottom chat 
var loadMore = function () {
    for (var i = 0; i < 5; i++) {
        var item = document.createElement('li');
        item.innerText = 'Item ' + nextItem++;
        messageList.appendChild(item);
    }
}

// Event Scroll Chat
messageList.addEventListener("scroll", (event) => {
    output.textContent = `scrollTop: ${messageList.scrollTop}`;
    if (messageList.scrollTop + messageList.clientHeight >= messageList.scrollHeight) {
        loadMore();
    }
    // Callback Observer API Intersection
    const boxes = document.querySelectorAll('.box');
    boxes.forEach(element => observer.observe(element));
});


const debug = document.querySelector('.debug');
const displayed = {};

function scrollTracking(entries) {
    for (const entry of entries) {
        displayed[entry.target.id] = entry.intersectionRatio >= 0.2;
    }
    debug.textContent = Object
        .entries(displayed)
        .filter(([id, inViewport]) => inViewport)
        .map(([id, inViewport]) => id)
        .join('\n');
}

const observer = new IntersectionObserver(scrollTracking, {
    threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
});
