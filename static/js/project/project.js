const row = document.getElementById('row')
const task_groups = document.querySelectorAll('.task_group:not(.new_task_group)')
const hidden_col = document.getElementById('hidden_col')
const headers = document.querySelectorAll('.task_group_header')
const tasks = document.querySelectorAll('.task:not(.new_task)')


var loc = window.location
var wsStart = 'ws://'
if (loc.protocol == 'https:') {
    wsStart = 'wss://'
}
var endpoint = wsStart + loc.host + loc.pathname
var socket = new ReconnectingWebSocket(endpoint)

window.onload = function colorizeTable() {
    task_groups.forEach(col => {
        col.style.backgroundColor = col.getAttribute('bkg_clr')
    })

    tasks.forEach(task => {
        task.style.backgroundColor = task.parentElement.getAttribute('task_bkg_color')
    })
}

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

task_groups.forEach(group => {
    group.addEventListener('dragover', e => {
        e.preventDefault()
        const task = document.querySelector('.dragging')
        if (task == null)
            return;
        var afterElement = getTaskDragAfterElement(group, e.clientY)
        if (afterElement == null)
            group.appendChild(task)
        else
            group.insertBefore(task, afterElement)
        task.style.backgroundColor = task.parentElement.getAttribute('task_bkg_color')
    })
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

headers.forEach(header => {
    header.addEventListener('dragstart', () => {
        header.parentNode.classList.add('dragging_group')
        draggingGroupOldPos = [...header.parentNode.parentNode.children].indexOf(header.parentNode);
    })

    header.addEventListener('dragend', () => {
        header.parentNode.classList.remove('dragging_group')
        socket.send(JSON.stringify(
            {
                'operation': 'move_task_group',
                'group_id': header.parentNode.getAttribute('id').split('_')[1],
                'new_pos': [...header.parentNode.parentNode.children].indexOf(header.parentNode)
            }));
    })
})

tasks.forEach(task => {
    task.addEventListener('dragstart', () => {
        task.classList.add('dragging')
        draggingTaskOldGroupPos = [...task.parentNode.parentNode.children].indexOf(task.parentNode);
        draggingTaskOldPos = [...task.parentNode.children].indexOf(task) - 1;
    })

    task.addEventListener('dragend', () => {
        task.classList.remove('dragging')
        socket.send(JSON.stringify(
            {
                'operation': 'move_task',
                'task_id': task.getAttribute('id').split('_')[1],
                'new_group_id': task.parentNode.getAttribute('id').split('_')[1],
                'new_pos': [...task.parentNode.children].indexOf(task) - 1
            }));
    })
})

function getTaskDragAfterElement(group, y) {
    const draggableElements = [...group.querySelectorAll('.task:not(.dragging')]

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

socket.onmessage = function (e) {
    // console.log('message', e)
    data = JSON.parse(e.data)

    if (data['operation'] == 'move_task_group') {
        if (data['new_pos'] >= row.childElementCount - 1)
            return

        var moved_group = document.getElementById('group_' + data['group_id'])
        if ([...moved_group.parentNode.children].indexOf(moved_group) >= data['new_pos'])
            var group_on_pos = row.children[data['new_pos']]
        else
            var group_on_pos = row.children[data['new_pos'] + 1]
        if (moved_group != group_on_pos)
            row.insertBefore(moved_group, group_on_pos)
    } else if (data['operation'] == 'move_task') {
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
}

socket.onopen = function (e) {
    // console.log('open', e)
}

socket.onclose = function (e) {
    // console.log('close', e)
}

socket.onerror = function (e) {
    // console.log('error', e)
}