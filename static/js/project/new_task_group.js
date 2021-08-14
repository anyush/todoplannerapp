const name_field = document.getElementById('id_name')
const group_color_picker = document.getElementById('id_color')
const task_color_picker = document.getElementById('id_task_color')
const button = document.getElementById('button')

const header = document.getElementById('header')
const group = document.getElementById('task_group')
const tasks = document.querySelectorAll('.task')


window.onload = function colorizeTable() {
    group.style.backgroundColor = group_color_picker.value
    tasks.forEach(task => {
        task.style.backgroundColor = task_color_picker.value
    })
}

name_field.addEventListener('input', e => {
    if (name_field.value != '')
        header.innerText = name_field.value
    else
        header.innerText = 'Task Group'
})

group_color_picker.addEventListener('input', e => {
    group.style.backgroundColor = group_color_picker.value
})

task_color_picker.addEventListener('input', e => {
    tasks.forEach(task => {
        task.style.backgroundColor = task_color_picker.value
    })
})
