// constants
const staticFilesSource = '/static/';

// grobal variables
var deletedTaskGroup = null;
var deletedTask = null;

// main elements
const row = document.getElementById('row');
const newGroupBtn = document.getElementById('newGroupBtn');
const hiddenCol = document.getElementById('hiddenCol');

// modal elements
const modal = document.getElementById('modal');
const modalBlocks = document.querySelectorAll('.modalContent');
const modalBlockModifyGroup = document.getElementById('groupCreation');
const modalBlockDeleteGroup = document.getElementById('groupDeletion');
const modalBlockModifyTask = document.getElementById('taskModalBlock');
//// task group form
const modifiableGroupModalBlockTitle = document.getElementById('modifiableGroupModalBlockTitle');
const modifiableGroupId = document.getElementById('modifiableGroupId');
const modifiableGroupTitle = document.getElementById('modifiableGroupName');
const modifiableGroupColorPicker = document.getElementById('modifiableGroupColor');
const modifiableGroupTaskColorPicker = document.getElementById('modifiableGroupTaskColor');
const modifiableGroupConfirmBtn = document.getElementById('modifiableGroupConfirm');
const modifiableGroupModifyBtn = document.getElementById('modifiableGroupModify');
const modifiableGroupCancelBtn = document.getElementById('modifiableGroupCancel');


const modifiableGroup = document.getElementById('modifiableGroup');
const modifiableGroupHeader = document.getElementById('modifiableGroupHeader');
const modifiableGroupTasks = modifiableGroup.querySelectorAll('.task');
//// task form
const modifiableTaskModalBlockTitle = document.getElementById('modifiableTaskModalBlockTitle');
const modifiableTaskId = document.getElementById('modifiableTaskId');
const modifiableTaskGroupId = document.getElementById('modifiableTaskGroupId');
const modifiableTaskTitle = document.getElementById('modifiableTaskName');
const modifiableTaskDescr = document.getElementById('modifiableTaskDescription');
const modifiableTaskDeadline = document.getElementById('modifiableTaskDeadlineHidden');
const modifiableTaskDeadlineDate = document.getElementById('modifiableTaskDeadlineDate');
const modifiableTaskDeadlineTime = document.getElementById('modifiableTaskDeadlineTime');
const modifiableTaskPerformers = document.getElementById('modifiableTaskPerformers');
const modifiableTaskConfirmBtn = document.getElementById('modifiableTaskConfirm');
const modifiableTaskModifyBtn = document.getElementById('modifiableTaskModify');
const modifiableTaskCancelBtn = document.getElementById('modifiableTaskCancel');
//// task group deletion
const deleteTitle = document.getElementById('deleteTitle');
const deleteQuestion = document.getElementById('deleteQuestion');
const cancelDeleteBtn = document.getElementById('cancelDelete');
const confirmDeleteBtn = document.getElementById('confirmDelete');



// socket configuration
var loc = window.location;
var wsStart = 'ws://';
if (loc.protocol == 'https:') {
    wsStart = 'wss://';
}
var endpoint = wsStart + loc.host + loc.pathname;
var socket = new ReconnectingWebSocket(endpoint);

socket.onmessage = function (e) {
    // console.log('message', e);
    data = JSON.parse(e.data);
    operation = data['operation'];
    context = JSON.parse(data['context']);
    messageHandlers[operation](context);
}

socket.onopen = function (e) {
    // console.log('open', e);
    socket.send(JSON.stringify({
        'operation': 'get_data',
        'context': '{}'
    }));
}

socket.onclose = function (e) {
    // console.log('close', e);
}

socket.onerror = function (e) {
    // console.log('error', e);
}



// socket message handlers
function removeAllTaskGroups() {
    while (row.firstChild != newGroupBtn.parentNode) {
        row.removeChild(row.firstChild);
    }
}

var messageHandlerGetProjectData = function (context) {
    context = context.reverse();
    removeAllTaskGroups();

    context.forEach(pair => {
        var groupData = JSON.parse(pair[0]);
        var tasks = pair[1];

        var groupElement = createGroupElement(groupData);

        var headerElement = createGroupHeaderElement(groupData['name'], groupElement);
        groupElement.appendChild(headerElement);

        tasks.forEach(task => {
            taskData = JSON.parse(task);
            var taskElement = createTaskElement(taskData, groupData['task_color']);
            groupElement.appendChild(taskElement);
        });

        var newTaskElement = createNewTaskElement(groupData['id']);
        groupElement.appendChild(newTaskElement);

        row.prepend(groupElement);
    });
}

const messageHandlerModifyTaskGroup = function (context) {
    var modifiedGroup = document.getElementById('group_' + context['group_id']);
    if (modifiedGroup == null) {
        socket.send(JSON.stringify({
            'operation': 'get_data',
            'context': '{}'
        }));
        return;
    }

    modifiedGroup.querySelector('.groupHeaderText').innerText = context['name'];
    modifiedGroup.setAttribute('bkgColor', context['color']);
    modifiedGroup.setAttribute('taskBkgColor', context['task_color']);
    modifiedGroup.style.backgroundColor = context['color'];
    var tasks = modifiedGroup.querySelectorAll('.task:not(.newTask)');
    tasks.forEach(task => {
        task.style.backgroundColor = context['task_color'];
    });
}

var messageHandlerMoveTaskGroup = function (context) {
    if (context['new_pos'] >= row.childElementCount - 1)
        return;

    var movedGroup = document.getElementById('group_' + context['group_id']);
    if ([...movedGroup.parentNode.children].indexOf(movedGroup) >= context['new_pos'])
        var groupOnPos = row.children[context['new_pos']];
    else
        var groupOnPos = row.children[context['new_pos'] + 1];
    if (movedGroup != groupOnPos)
        row.insertBefore(movedGroup, groupOnPos);
}

var messageHandlerMoveTask = function (context) {
    var movedTask = document.getElementById('task_' + context['task_id']);
    var newGroup = document.getElementById('group_' + context['new_group_id']);

    if (context['new_pos'] < newGroup.childElementCount - 1) {
        if (movedTask.parentNode == newGroup && [...movedTask.parentNode.children].indexOf(movedTask) < context['new_pos'] + 1)
            var taskOnPosition = newGroup.children[context['new_pos'] + 2];
        else
            var taskOnPosition = newGroup.children[context['new_pos'] + 1];
        if (movedTask.parentNode == newGroup && taskOnPosition == movedTask)
            return;

        newGroup.insertBefore(movedTask, taskOnPosition);
    } else {
        newGroup.appendChild(movedTask);
    }
    movedTask.style.backgroundColor = movedTask.parentElement.getAttribute('taskBkgColor');
}

var messageHandlerDeleteTaskGroup = function (context) {
    var deletedGroup = document.getElementById('group_' + context['group_id']);

    if (deletedGroup != null)
        deletedGroup.parentNode.removeChild(deletedGroup);
}

const messageHandlers = {
    'get_data': messageHandlerGetProjectData,
    'modify_task_group': messageHandlerModifyTaskGroup,
    'move_task_group': messageHandlerMoveTaskGroup,
    'move_task': messageHandlerMoveTask,
    'delete_task_group': messageHandlerDeleteTaskGroup,
}



// window configuration
window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

window.onload = function () {
    modifiableGroup.style.backgroundColor = modifiableGroupColorPicker.value;
    modifiableGroupTasks.forEach(task => {
        task.style.backgroundColor = modifiableGroupTaskColorPicker.value;
    })
}



// page elements generation
function createGroupElement(groupData) {
    var groupElement = document.createElement('td');
    groupElement.id = 'group_' + groupData['id'];
    groupElement.classList.add('taskGroup');
    groupElement.setAttribute('bkgColor', groupData['color']);
    groupElement.setAttribute('taskBkgColor', groupData['task_color']);
    groupElement.style.backgroundColor = groupData['color'];

    groupElement.addEventListener('dragover', e => {
        e.preventDefault();
        const task = document.querySelector('.dragging');
        if (task == null)
            return;
        var afterElement = getTaskDragAfterElement(groupElement, e.clientY);
        if (afterElement == null)
            afterElement = document.getElementById('newTask_' + groupData['id']);
        groupElement.insertBefore(task, afterElement);
        task.style.backgroundColor = task.parentElement.getAttribute('taskBkgColor');
    });

    return groupElement;
}

function hideModalContent() {
    modalBlocks.forEach((block) => {
        block.style.display = 'none';
    });
}

function createGroupHeaderDeleteBtn() {
    var deleteButtonElement = document.createElement('button');
    deleteButtonElement.classList.add('groupHeaderButton');
    deleteButtonElement.style.backgroundImage = 'url(' + loc.origin + staticFilesSource + 'png/project/deleteButton.png)';
    deleteButtonElement.addEventListener('click', () => {
        hideModalContent();
        modal.style.display = 'block';
        modalBlockDeleteGroup.style.display = 'block';

        deleteTitle.innerText = 'Delete Task Group';
        deleteQuestion.innerText = 'Are you sure you want to delete "' + deleteButtonElement.parentNode.innerText + '"?';
        deletedTaskGroup = deleteButtonElement.parentNode.parentNode;
    });

    return deleteButtonElement;
}

function createGroupHeaderModifyBtn() {
    var modifyButtonElement = document.createElement('button');
    modifyButtonElement.classList.add('groupHeaderButton');
    modifyButtonElement.style.backgroundImage = 'url(' + loc.origin + staticFilesSource + 'png/project/settingsButton.png)';
    modifyButtonElement.addEventListener('click', () => {
        hideModalContent();

        modal.style.display = 'block';
        modalBlockModifyGroup.style.display = 'block';

        modifiableGroupModalBlockTitle.innerText = 'Modify Task Group';
        modifiableGroupTitle.value = modifyButtonElement.parentNode.innerText;
        modifiableGroupHeader.innerText = modifyButtonElement.parentNode.innerText;
        modifiableGroupColorPicker.value = modifyButtonElement.parentNode.parentNode.getAttribute('bkgColor');
        modifiableGroup.style.backgroundColor = modifiableGroupColorPicker.value;
        modifiableGroupTaskColorPicker.value = modifyButtonElement.parentNode.parentNode.getAttribute('taskBkgColor');
        modifiableGroupTasks.forEach(task => {
            task.style.backgroundColor = modifiableGroupTaskColorPicker.value;
        });
        modifiableGroupConfirmBtn.style.display = 'none';
        modifiableGroupModifyBtn.style.display = 'inline';
        modifiableGroupId.value = parseInt(modifyButtonElement.parentNode.parentNode.getAttribute('id').split('_')[1]);
    });

    return modifyButtonElement;
}

function createGroupHeaderElement(name, groupNode) {
    var headerElement = document.createElement('div');
    headerElement.classList.add('taskGroupHeader');
    headerElement.setAttribute('draggable', 'true');
    headerElement.innerHTML = '<span class="groupHeaderText">' + name + '</span>';

    var deleteButtonElement = createGroupHeaderDeleteBtn();
    headerElement.appendChild(deleteButtonElement);

    var settingsButtonElement = createGroupHeaderModifyBtn();
    headerElement.appendChild(settingsButtonElement);

    headerElement.addEventListener('dragstart', () => {
        headerElement.parentNode.classList.add('draggingGroup');
    });

    headerElement.addEventListener('dragend', () => {
        headerElement.parentNode.classList.remove('draggingGroup');
        socket.send(JSON.stringify({
            'operation': 'move_task_group',
            'context': JSON.stringify({
                'group_id': parseInt(headerElement.parentNode.getAttribute('id').split('_')[1]),
                'new_pos': parseInt([...headerElement.parentNode.parentNode.children].indexOf(headerElement.parentNode))
            })
        }));
    });

    return headerElement;
}

function createTaskModifyBtn() {
    var modifyButtonElement = createGroupHeaderModifyBtn()

    modifyButtonElement.addEventListener('click', () => {
        hideModalContent();

        modal.style.display = 'block';
        modalBlockModifyTask.style.display = 'block';

        modifiableTaskModalBlockTitle.innerText = 'Modify Task';
        modifiableTaskTitle.value = modifyButtonElement.parentNode.innerText;
        modifiableTaskConfirmBtn.style.display = 'none';
        modifiableTaskModifyBtn.style.display = 'inline';
        modifiableTaskId.value = parseInt(modifyButtonElement.parentNode.getAttribute('id').split('_')[1]);
    });

    return modifyButtonElement;
}

function createTaskDeleteBtn() {
    var deleteButtonElement = createGroupHeaderDeleteBtn();

    deleteButtonElement.addEventListener('click', () => {
        hideModalContent();
        modal.style.display = 'block';
        modalBlockDeleteGroup.style.display = 'block';

        deleteTitle.innerText = 'Delete Task';
        deleteQuestion.innerText = 'Are you sure you want to delete "' + deleteButtonElement.parentNode.innerText + '"?';
        deletedTask = deleteButtonElement.parentNode;
    });

    return deleteButtonElement;
}

function createTaskHeaderElement(name) {
    var headerElement = document.createElement('div');
    headerElement.classList.add('taskHeader');
    headerElement.innerHTML = '<span class="taskHeaderText">' + name + '</span>';

    var deleteButtonElement = createTaskDeleteBtn();
    headerElement.appendChild(deleteButtonElement);

    var settingsButtonElement = createTaskModifyBtn();
    headerElement.appendChild(settingsButtonElement);

    return headerElement;
}

function createTaskElement(taskData, color) {
    var taskElement = document.createElement('div');
    taskElement.id = 'task_' + taskData['id'];
    taskElement.classList.add('task');
    taskElement.setAttribute('draggable', 'true');
    taskElement.style.backgroundColor = color;

    taskElement.appendChild(createTaskHeaderElement(taskData['name']));
    taskElement.innerHTML += '<hr /><div class="taskDescr">' + taskData['description'] + '</div>';

    taskElement.addEventListener('dragstart', () => {
        taskElement.classList.add('dragging');
    });

    taskElement.addEventListener('dragend', () => {
        taskElement.classList.remove('dragging');
        socket.send(JSON.stringify({
            'operation': 'move_task',
            'context': JSON.stringify({
                'task_id': parseInt(taskElement.getAttribute('id').split('_')[1]),
                'new_group_id': parseInt(taskElement.parentNode.getAttribute('id').split('_')[1]),
                'new_pos': parseInt([...taskElement.parentNode.children].indexOf(taskElement) - 1)
            })
        }));
    });

    return taskElement;
}

function createNewTaskElement(groupId) {
    var newTaskElement = document.createElement('button');
    newTaskElement.type = 'submit';
    newTaskElement.id = 'newTask_' + groupId;
    newTaskElement.classList.add('task');
    newTaskElement.classList.add('newTask');
    newTaskElement.innerText = 'New Task';

    newTaskElement.addEventListener('click', () => {
        hideModalContent();
        modal.style.display = 'block';
        modalBlockModifyTask.style.display = 'block';

        modifiableTaskModalBlockTitle.innerText = 'Create new Task';
        modifiableTaskGroupId.value = newTaskElement.parentNode.getAttribute('id').split('_')[1];
        modifiableTaskTitle.value = '';
        modifiableTaskDescr.value = '';
        modifiableTaskDeadlineDate.value = '';
        modifiableTaskDeadlineTime.value = '';
        modifiableTaskConfirmBtn.style.display = 'inline';
        modifiableTaskModifyBtn.style.display = 'none';
    })

    return newTaskElement;
}



// drag-and-drop logic
row.addEventListener('dragover', e => {
    e.preventDefault();
    var group = document.querySelector('.draggingGroup');
    if (group == null)
        return;
    var afterGroup = getGroupDragAfterElement(e.clientX);
    if (afterGroup == null)
        row.insertBefore(group, newGroupBtn.parentNode);
    else
        row.insertBefore(group, afterGroup);
})

function getGroupDragAfterElement(x) {
    var draggableElements = [...row.querySelectorAll('.taskGroup:not(.draggingGroup):not(.newTaskGroup):not(#modifiableGroup)')];

    return draggableElements.reduce((closest, child) => {
        var box = child.getBoundingClientRect();
        var offset = x - box.right + box.width / 2;
        if (offset < 0 && offset > closest.offset)
            return { offset: offset, element: child };
        else
            return closest;
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

function getTaskDragAfterElement(group, y) {
    const draggableElements = [...group.querySelectorAll('.task:not(.dragging):not(.modifiableGroupTask)')];

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset)
            return { offset: offset, element: child };
        else
            return closest;
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}



// task group creation/modification form logic
newGroupBtn.addEventListener('click', e => {
    hideModalContent();
    modal.style.display = 'block';
    modalBlockModifyGroup.style.display = 'block';

    modifiableGroupModalBlockTitle.innerText = 'Create new Task Group';
    modifiableGroupTitle.value = '';
    modifiableGroupHeader.innerText = 'Task Group';
    modifiableGroupColorPicker.value = modifiableGroupColorPicker.getAttribute('default');
    modifiableGroup.style.backgroundColor = modifiableGroupColorPicker.value;
    modifiableGroupTaskColorPicker.value = modifiableGroupTaskColorPicker.getAttribute('default');
    modifiableGroupTasks.forEach(task => {
        task.style.backgroundColor = modifiableGroupTaskColorPicker.value;
    });
    modifiableGroupConfirmBtn.style.display = 'inline';
    modifiableGroupModifyBtn.style.display = 'none';
});

modifiableGroupTitle.addEventListener('input', e => {
    if (modifiableGroupTitle.value != '')
        modifiableGroupHeader.innerText = modifiableGroupTitle.value;
    else
        modifiableGroupHeader.innerText = 'Task Group';
});

modifiableGroupColorPicker.addEventListener('input', e => {
    modifiableGroup.style.backgroundColor = modifiableGroupColorPicker.value;
});

modifiableGroupTaskColorPicker.addEventListener('input', e => {
    modifiableGroupTasks.forEach(task => {
        task.style.backgroundColor = modifiableGroupTaskColorPicker.value;
    });
});

modifiableGroupCancelBtn.addEventListener('click', e => {
    modal.style.display = 'none';
});

modifiableGroupModifyBtn.addEventListener('click', e => {
    socket.send(JSON.stringify({
        'operation': 'modify_task_group',
        'context': JSON.stringify({
            'group_id': parseInt(modifiableGroupId.value),
            'name': modifiableGroupTitle.value,
            'color': modifiableGroupColorPicker.value,
            'task_color': modifiableGroupTaskColorPicker.value
        })
    }));
    modal.style.display = 'none';
});

modifiableGroupConfirmBtn.addEventListener('click', e => {
    socket.send(JSON.stringify({
        'operation': 'create_task_group',
        'context': JSON.stringify({
            'name': modifiableGroupTitle.value,
            'color': modifiableGroupColorPicker.value,
            'task_color': modifiableGroupTaskColorPicker.value
        })
    }));
    modal.style.display = 'none';
});


// task creation/modification logic
modifiableTaskCancelBtn.addEventListener('click', e => {
    modal.style.display = 'none';
});

modifiableTaskConfirmBtn.addEventListener('click', e => {
    if (modifiableTaskDeadlineDate.value == '' ^ modifiableTaskDeadlineTime.value == '')
        return;

    var context = {
        'name': modifiableTaskTitle.value,
        'description': modifiableTaskDescr.value,
        'group_id': parseInt(modifiableTaskGroupId.value),
        'performers': Array.from(modifiableTaskPerformers.selectedOptions).map(({ value }) => parseInt(value))
    };

    var deadline = modifiableTaskDeadlineDate.value + ' ' + modifiableTaskDeadlineTime.value;
    if (deadline != ' ')
        context['deadline_time'] = deadline;


    socket.send(JSON.stringify({
        'operation': 'create_task',
        'context': JSON.stringify(context)
    }));
    modal.style.display = 'none';
});


// task group/task deletion logic
cancelDeleteBtn.addEventListener('click', () => {
    modal.style.display = 'none';
    deletedTaskGroup = null;
    deletedTask = null;
});

confirmDeleteBtn.addEventListener('click', () => {
    if (!(deletedTaskGroup == null ^ deletedTask == null)) {
        cancelDeleteBtn.click();
        return;
    }

    if (deletedTaskGroup != null) {
        socket.send(JSON.stringify({
            'operation': 'delete_task_group',
            'context': JSON.stringify({
                'group_id': parseInt(deletedTaskGroup.getAttribute('id').split('_')[1])
            })
        }));
        row.removeChild(deletedTaskGroup);
    } else {
        socket.send(JSON.stringify({
            'operation': 'delete_task',
            'context': JSON.stringify({
                'task_id': parseInt(deletedTask.getAttribute('id').split('_')[1])
            })
        }));
        deletedTask.parentNode.removeChild(deletedTask);
    }

    cancelDeleteBtn.click();
});



// secondary functions
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
