const row = document.getElementById('row')
const hidden_col = document.getElementById('hidden_col')


var loc = window.location
var wsStart = 'ws://'
if (loc.protocol == 'https:') {
    wsStart = 'wss://'
}
var endpoint = wsStart + loc.host + loc.pathname
var socket = new ReconnectingWebSocket(endpoint)

row.addEventListener('dragover', e => {
    e.preventDefault()
    const group = document.querySelector('.dragging_group')
    if (group == null)
        return;
    const afterGroup = getGroupDragAfterElement(e.clientX)
    if (afterGroup == null) {
        row.insertBefore(group, hidden_col)
    } else {
        row.insertBefore(group, afterGroup)
    }
})

function getGroupDragAfterElement(x) {
    const draggableElements = [...row.querySelectorAll('.task_group:not(.dragging_group')]

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect()
        const offset = x - box.right + box.width / 2
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child }
        } else {
            return closest
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element
}

function getTaskDragAfterElement(group, y) {
    const draggableElements = [...group.querySelectorAll('.task:not(.dragging)')]

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect()
        const offset = y - box.top - box.height / 2
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child }
        } else {
            return closest
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element
}

function sendAJAX(data, url) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    xhttp.send(data);
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function removeAllTaskGroups() {
    while (row.firstChild != document.getElementById('new_group')) {
        row.removeChild(row.firstChild);
    }
}


function createGroupElement(groupData) {
    var groupElement = document.createElement('td')
    groupElement.id = 'group_' + groupData['id']
    groupElement.classList.add('task_group')
    groupElement.setAttribute('task_bkg_color', groupData['task_color'])
    groupElement.style.backgroundColor = groupData['color']


    groupElement.addEventListener('dragover', e => {
        e.preventDefault()
        const task = document.querySelector('.dragging')
        if (task == null)
            return;
        var afterElement = getTaskDragAfterElement(groupElement, e.clientY)
        if (afterElement == null)
            afterElement = document.getElementById('new_task_' + groupData['id'])
        groupElement.insertBefore(task, afterElement)
        task.style.backgroundColor = task.parentElement.getAttribute('task_bkg_color')
    })

    return groupElement
}

function createHeaderElement(name) {
    var headerElement = document.createElement('div')
    headerElement.classList.add('task_group_header')
    headerElement.setAttribute('draggable', 'true')
    headerElement.innerText = name
    
    headerElement.addEventListener('dragstart', () => {
        headerElement.parentNode.classList.add('dragging_group')
    })

    headerElement.addEventListener('dragend', () => {
        headerElement.parentNode.classList.remove('dragging_group')
        socket.send(JSON.stringify(
            {
                'operation': 'move_task_group',
                'group_id': headerElement.parentNode.getAttribute('id').split('_')[1],
                'new_pos': [...headerElement.parentNode.parentNode.children].indexOf(headerElement.parentNode)
            }));
    })

    return headerElement
}

function createTaskElement(taskData, color) {
    var taskElement = document.createElement('div')
    taskElement.id = 'task_' + taskData['id']
    taskElement.classList.add('task')
    taskElement.setAttribute('draggable', 'true')
    taskElement.style.backgroundColor = color
    taskElement.innerHTML = taskData['name'] + '<hr />' + taskData['description']

    taskElement.addEventListener('dragstart', () => {
        taskElement.classList.add('dragging')
    })

    taskElement.addEventListener('dragend', () => {
        taskElement.classList.remove('dragging')
        socket.send(JSON.stringify(
            {
                'operation': 'move_task',
                'task_id': taskElement.getAttribute('id').split('_')[1],
                'new_group_id': taskElement.parentNode.getAttribute('id').split('_')[1],
                'new_pos': [...taskElement.parentNode.children].indexOf(taskElement) - 1
            }));
    })

    return taskElement
}

function createNewTaskElement(groupId) {
    var newTaskElement = document.createElement('button')
    newTaskElement.type = 'submit'
    newTaskElement.id = 'new_task_' + groupId
    newTaskElement.classList.add('task')
    newTaskElement.classList.add('new_task')
    newTaskElement.innerText = 'New Task'

    return newTaskElement
}

var messageHandlerGetProjectData = function (data) {
    data = JSON.parse(data['context']).reverse()
    removeAllTaskGroups()
    
    data.forEach(pair => {
        var groupData = JSON.parse(pair[0])
        var tasks = pair[1]

        var groupElement = createGroupElement(groupData)

        var headerElement = createHeaderElement(groupData['name'])
        groupElement.appendChild(headerElement)

        tasks.forEach(task => {
            taskData = JSON.parse(task)
            var taskElement = createTaskElement(taskData, groupData['task_color'])
            groupElement.appendChild(taskElement)
        })

        var newTaskElement = createNewTaskElement(groupData['id'])
        groupElement.appendChild(newTaskElement)

        row.prepend(groupElement)
    })
}

var messageHandlerAddTaskGroup = function () {
    socket.send({
        'operation': 'get_project_data'
    })
}

var messageHandlerMoveTaskGroup = function (data) {
    if (data['new_pos'] >= row.childElementCount - 1)
        return

    var moved_group = document.getElementById('group_' + data['group_id'])
    if ([...moved_group.parentNode.children].indexOf(moved_group) >= data['new_pos'])
        var group_on_pos = row.children[data['new_pos']]
    else
        var group_on_pos = row.children[data['new_pos'] + 1]
    if (moved_group != group_on_pos)
        row.insertBefore(moved_group, group_on_pos)
}

var messageHandlerMoveTask = function (data) {
    var moved_task = document.getElementById('task_' + data['task_id'])
    var new_group = document.getElementById('group_' + data['new_group_id'])

    if (data['new_pos'] < new_group.childElementCount - 1) {
        if (moved_task.parentNode == new_group && [...moved_task.parentNode.children].indexOf(moved_task) < data['new_pos'] + 1)
            var task_on_position = new_group.children[data['new_pos'] + 2]
        else
            var task_on_position = new_group.children[data['new_pos'] + 1]
        if (moved_task.parentNode == new_group && task_on_position == moved_task)
            return

        new_group.insertBefore(moved_task, task_on_position)
    } else {
        new_group.appendChild(moved_task)
    }
    moved_task.style.backgroundColor = moved_task.parentElement.getAttribute('task_bkg_color')
}

const messageHandlers = {
    'get_data': messageHandlerGetProjectData,
    'move_task_group': messageHandlerMoveTaskGroup,
    'move_task': messageHandlerMoveTask,
    'add_task_group': messageHandlerAddTaskGroup,
}

socket.onmessage = function (e) {
    // console.log('message', e)
    data = JSON.parse(e.data)
    messageHandlers[data['operation']](data)
}

socket.onopen = function (e) {
    // console.log('open', e)
    socket.send(JSON.stringify({
        'operation': 'get_data'
    }))
}

socket.onclose = function (e) {
    // console.log('close', e)
}

socket.onerror = function (e) {
    // console.log('error', e)
}