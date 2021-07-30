const row = document.getElementById('row')
const cols = document.querySelectorAll('.task_column')
const hidden_col = document.getElementById('hidden_col')
const headers = document.querySelectorAll('.task_column_header')
const tasks = document.querySelectorAll('.task')

var draggingGroupOldPos;

var draggingTaskOldGroupPos;
var draggingTaskOldPos;

window.onload = function colorizeTable() {
    cols.forEach(col => {
        col.style.backgroundColor = col.getAttribute('bkg_clr')
    })

    tasks.forEach(task => {
        task.style.backgroundColor = task.parentElement.getAttribute('task_bkg_color')
    })
}

row.addEventListener('dragover', e => {
    e.preventDefault()
    const col = document.querySelector('.dragging_col')
    if (col == null)
        return;
    const afterCol = getColDragAfterElement(e.clientX)
    if (afterCol == null) {
        row.insertBefore(col, hidden_col)
    } else {
        row.insertBefore(col, afterCol)
    }
})

cols.forEach(col => {
    col.addEventListener('dragover', e => {
        e.preventDefault()
        const task = document.querySelector('.dragging')
        if (task == null)
            return;
        var afterElement = getTaskDragAfterElement(col, e.clientY)
        if (afterElement == null)
            col.appendChild(task)
        else
            col.insertBefore(task, afterElement)
        task.style.backgroundColor = task.parentElement.getAttribute('task_bkg_color')
    })
})

function getColDragAfterElement(x) {
    const draggableElements = [...row.querySelectorAll('.task_column:not(.dragging_col')]

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
        header.parentNode.classList.add('dragging_col')
        draggingGroupOldPos = [...header.parentNode.parentNode.children].indexOf(header.parentNode);
    })

    header.addEventListener('dragend', () => {
        header.parentNode.classList.remove('dragging_col')
        sendDataToServer(JSON.stringify(
            {
                'old_pos': draggingGroupOldPos,
                'new_pos': [...header.parentNode.parentNode.children].indexOf(header.parentNode)
            }), "mv_col/");
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
        sendDataToServer(JSON.stringify(
            {
                'old_group_pos': draggingTaskOldGroupPos,
                'new_group_pos': [...task.parentNode.parentNode.children].indexOf(task.parentNode),
                'old_pos': draggingTaskOldPos,
                'new_pos': [...task.parentNode.children].indexOf(task) - 1
            }), "mv_task/");
    })
})

function getTaskDragAfterElement(col, y) {
    const draggableElements = [...col.querySelectorAll('.task:not(.dragging')]

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



function sendDataToServer(data, url="") {
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