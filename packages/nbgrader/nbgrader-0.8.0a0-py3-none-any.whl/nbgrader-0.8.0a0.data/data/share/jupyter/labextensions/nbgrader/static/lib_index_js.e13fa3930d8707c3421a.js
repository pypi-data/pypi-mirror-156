"use strict";
(self["webpackChunknbgrader"] = self["webpackChunknbgrader"] || []).push([["lib_index_js"],{

/***/ "./lib/assignment_list/assignmentlist.js":
/*!***********************************************!*\
  !*** ./lib/assignment_list/assignmentlist.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "AssignmentList": () => (/* binding */ AssignmentList),
/* harmony export */   "CourseList": () => (/* binding */ CourseList),
/* harmony export */   "requestAPI": () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _common_validate__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../common/validate */ "./lib/common/validate.js");






class AssignmentList {
    constructor(widget, released_selector, fetched_selector, submitted_selector, options, app) {
        this.list_loading_ids = ['released_assignments_list_loading', 'fetched_assignments_list_loading', 'submitted_assignments_list_loading'];
        this.list_placeholder_ids = ['released_assignments_list_placeholder', 'fetched_assignments_list_placeholder', 'submitted_assignments_list_placeholder'];
        this.list_error_ids = ['released_assignments_list_error', 'fetched_assignments_list_error', 'submitted_assignments_list_error'];
        this.released_selector = released_selector;
        this.fetched_selector = fetched_selector;
        this.submitted_selector = submitted_selector;
        var div_elements = widget.node.getElementsByTagName('div');
        this.released_element = div_elements.namedItem(released_selector);
        this.fetched_element = div_elements.namedItem(fetched_selector);
        this.submitted_element = div_elements.namedItem(submitted_selector);
        this.options = options;
        this.base_url = options.get('base_url') || _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl();
        this.app = app;
        this.callback = undefined;
    }
    clear_list(loading) {
        var elems = [this.released_element, this.fetched_element, this.submitted_element];
        var i;
        var j;
        // remove list items
        for (i = 0; i < elems.length; i++) {
            for (j = 0; j < elems[i].children.length; ++j) {
                if (elems[i].children[j].classList.contains('list_item')) {
                    elems[i].removeChild(elems[i].children[j]);
                    --j;
                }
            }
            if (loading) {
                // show loading
                elems[i].children.namedItem(this.list_loading_ids[i]).hidden = false;
                // hide placeholders and errors
                elems[i].children.namedItem(this.list_placeholder_ids[i]).hidden = true;
                elems[i].children.namedItem(this.list_error_ids[i]).hidden = true;
            }
            else {
                // show placeholders display
                elems[i].children.namedItem(this.list_placeholder_ids[i]).hidden = false;
                // hide loading and errors
                elems[i].children.namedItem(this.list_loading_ids[i]).hidden = true;
                elems[i].children.namedItem(this.list_error_ids[i]).hidden = true;
            }
        }
    }
    ;
    load_list_success(data) {
        this.clear_list(false);
        var len = data.length;
        for (var i = 0; i < len; i++) {
            var element = document.createElement('div');
            new Assignment(element, data[i], this.fetched_selector, (newData) => { this.handle_load_list(newData); }, this.options, this.app);
            if (data[i].status === 'released') {
                this.released_element.append(element);
                this.released_element.children.namedItem('released_assignments_list_placeholder').hidden = true;
            }
            else if (data[i]['status'] === 'fetched') {
                this.fetched_element.append(element);
                this.fetched_element.children.namedItem('fetched_assignments_list_placeholder').hidden = true;
            }
            else if (data[i]['status'] === 'submitted') {
                this.submitted_element.append(element);
                this.submitted_element.children.namedItem('submitted_assignments_list_placeholder').hidden = true;
            }
        }
        var assignments = this.fetched_element.getElementsByClassName('assignment-notebooks-link');
        for (let a of assignments) {
            var icon = document.createElement('i');
            icon.classList.add('fa', 'fa-caret-right');
            a.append(icon);
            a.onclick = function (event) {
                if (a.children[0].classList.contains('fa-caret-right')) {
                    a.children[0].classList.remove('fa-caret-right');
                    a.children[0].classList.add('fa-caret-down');
                }
                else {
                    a.children[0].classList.remove('fa-caret-down');
                    a.children[0].classList.add('fa-caret-right');
                }
                /* Open or close collapsed child list on click */
                const list_item = event.target.closest('.list_item');
                list_item.querySelector('.collapse').classList.toggle('in');
            };
        }
        if (this.callback) {
            this.callback();
            this.callback = undefined;
        }
    }
    ;
    show_error(error) {
        var elems = [this.released_element, this.fetched_element, this.submitted_element];
        var i;
        // remove list items
        for (i = 0; i < elems.length; i++) {
            for (var j = 0; j < elems[i].children.length; ++j) {
                if (elems[i].children[j].classList.contains('list_item')) {
                    elems[i].removeChild(elems[i].children[j]);
                    --j;
                }
            }
            // show errors
            elems[i].children.namedItem(this.list_error_ids[i]).hidden = false;
            elems[i].children.namedItem(this.list_error_ids[i]).innerText = error;
            // hide loading and placeholding
            elems[i].children.namedItem(this.list_loading_ids[i]).hidden = true;
            elems[i].children.namedItem(this.list_placeholder_ids[i]).hidden = true;
        }
    }
    ;
    handle_load_list(data) {
        if (data.success) {
            this.load_list_success(data.value);
        }
        else {
            this.show_error(data.value);
        }
    }
    ;
    async load_list(course, callback) {
        this.callback = callback;
        this.clear_list(true);
        try {
            const data = await requestAPI('assignments?course_id=' + course, {
                method: 'GET',
            });
            this.handle_load_list(data);
        }
        catch (reason) {
            console.error(`Error on GET /assignments.\n${reason}`);
        }
    }
    ;
}
;
class Assignment {
    constructor(element, data, parent, on_refresh, options, app) {
        this.element = element;
        this.data = data;
        this.parent = parent;
        this.on_refresh = on_refresh;
        this.options = options;
        this.base_url = options.get('base_url') || _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl();
        this.app = app;
        this.style();
        this.make_row();
    }
    style() {
        this.element.classList.add('list_item', "row");
    }
    ;
    escape_id() {
        // construct the id from the course id and the assignment id, and also
        // prepend the id with "nbgrader" (this also ensures that the first
        // character is always a letter, as required by HTML 4)
        var id = "nbgrader-" + this.data['course_id'] + "-" + this.data['assignment_id'];
        // replace spaces with '_'
        id = id.replace(/ /g, "_");
        // remove any characters that are invalid in HTML div ids
        id = id.replace(/[^A-Za-z0-9\-_]/g, "");
        return id;
    }
    ;
    make_link() {
        var container = document.createElement('span');
        ;
        container.classList.add('item_name', 'col-sm-6');
        var link;
        if (this.data['status'] === 'fetched') {
            link = document.createElement('a');
            var id = this.escape_id();
            link.classList.add('collapsed', 'assignment-notebooks-link');
            link.setAttribute('role', 'button');
            link.setAttribute('data-toggle', 'collapse');
            link.setAttribute('data-parent', this.parent);
            link.setAttribute('href', '#' + id);
            link.setAttribute('aria-expanded', 'false');
            link.setAttribute('aria-controls', id);
        }
        else {
            link = document.createElement('span');
        }
        link.innerText = (this.data['assignment_id']);
        container.append(link);
        return container;
    }
    ;
    submit_error(data) {
        const body_title = react__WEBPACK_IMPORTED_MODULE_3__.createElement('p', null, 'Assignment not submitted:');
        const body_content = react__WEBPACK_IMPORTED_MODULE_3__.createElement('pre', null, data.value);
        const body = react__WEBPACK_IMPORTED_MODULE_3__.createElement("div", { 'id': 'submission-message' }, [body_title, body_content]);
        (0,_common_validate__WEBPACK_IMPORTED_MODULE_4__.showNbGraderDialog)({
            title: "Invalid Submission",
            body: body,
            buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.Dialog.okButton()]
        }, true);
    }
    ;
    make_button() {
        var container = document.createElement('span');
        container.classList.add('item_status', 'col-sm-4');
        var button = document.createElement('button');
        button.classList.add('btn', 'btn-primary', 'btn-xs');
        container.append(button);
        var that = this;
        if (this.data['status'] === 'released') {
            button.innerText = "fetch";
            button.onclick = async function () {
                button.innerText = 'Fetching...';
                button.setAttribute('disabled', 'disabled');
                const dataToSend = { 'course_id': that.data['course_id'], 'assignment_id': that.data['assignment_id'] };
                try {
                    const reply = await requestAPI('assignments/fetch', {
                        body: JSON.stringify(dataToSend),
                        method: 'POST'
                    });
                    that.on_refresh(reply);
                }
                catch (reason) {
                    remove_children(container);
                    container.innerText = 'Error fetching assignment.';
                    console.error(`Error on POST /assignment_list/fetch ${dataToSend}.\n${reason}`);
                }
            };
        }
        else if (this.data.status == 'fetched') {
            button.innerText = "Submit";
            button.onclick = async function () {
                button.innerText = 'submitting...';
                button.setAttribute('disabled', 'disabled');
                const dataToSend = { course_id: that.data['course_id'], assignment_id: that.data['assignment_id'] };
                try {
                    const reply = await requestAPI('assignments/submit', {
                        body: JSON.stringify(dataToSend),
                        method: 'POST'
                    });
                    if (!reply.success) {
                        that.submit_error(reply);
                        button.innerText = 'Submit';
                        button.removeAttribute('disabled');
                    }
                    else {
                        that.on_refresh(reply);
                    }
                }
                catch (reason) {
                    remove_children(container);
                    container.innerText = 'Error submitting assignment.';
                    console.error(`Error on POST /assignment_list/assignments/submit ${dataToSend}.\n${reason}`);
                }
            };
        }
        else if (this.data.status == 'submitted') {
            button.innerText = "Fetch Feedback";
            button.onclick = async function () {
                button.innerText = 'Fetching Feedback...';
                button.setAttribute('disabled', 'disabled');
                const dataToSend = { course_id: that.data['course_id'], assignment_id: that.data['assignment_id'] };
                try {
                    const reply = await requestAPI('assignments/fetch_feedback', {
                        body: JSON.stringify(dataToSend),
                        method: 'POST'
                    });
                    that.on_refresh(reply);
                }
                catch (reason) {
                    remove_children(container);
                    container.innerText = 'Error fetching feedback.';
                    console.error(`Error on POST /assignments/fetch_feedback ${dataToSend}.\n${reason}`);
                }
            };
        }
        return container;
    }
    ;
    make_row() {
        var row = document.createElement('div');
        row.classList.add('col-md-12');
        var link = this.make_link();
        row.append(link);
        var s = document.createElement('span');
        s.classList.add('item_course', 'col-sm-2');
        s.innerText = this.data['course_id'];
        row.append(s);
        var id, element;
        var children = document.createElement('div');
        if (this.data['status'] == 'submitted') {
            id = this.escape_id() + '-submissions';
            children.id = id;
            children.classList.add('panel-collapse', 'list_container', 'assignment-notebooks');
            children.setAttribute('role', 'tabpanel');
            var d = document.createElement('div');
            d.classList.add('list_item', 'row');
            children.append(d);
            for (var i = 0; i < this.data['submissions'].length; i++) {
                element = document.createElement('div');
                new Submission(element, this.data.submissions[i], this.options, this.app);
                children.append(element);
            }
        }
        else if (this.data['status'] === 'fetched') {
            id = this.escape_id();
            children.id = id;
            children.classList.add('panel-collapse', 'list_container', 'assignment-notebooks', 'collapse');
            children.setAttribute('role', 'tabpanel');
            var d = document.createElement('div');
            d.classList.add('list_item', 'row');
            children.append(d);
            for (var i = 0; i < this.data['notebooks'].length; i++) {
                element = document.createElement('div');
                this.data.notebooks[i]['course_id'] = this.data['course_id'];
                this.data.notebooks[i]['assignment_id'] = this.data['assignment_id'];
                new Notebook(element, this.data.notebooks[i], this.options, this.app);
                children.append(element);
            }
        }
        row.append(this.make_button());
        this.element.innerHTML = '';
        this.element.append(row);
        this.element.append(children);
    }
    ;
}
;
const remove_children = function (element) {
    element.innerHTML = '';
};
class Submission {
    constructor(element, data, options, app) {
        this.element = element;
        this.data = data;
        this.options = options;
        this.base_url = options.get('base_url') || _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl();
        this.app = app;
        this.style();
        this.make_row();
    }
    style() {
        this.element.classList.add('list_item', 'row', 'nested_list_item');
    }
    ;
    make_row() {
        var container = document.createElement('div');
        container.classList.add('col-md-12');
        var status = document.createElement('span');
        status.classList.add('item_name', 'col-sm-6');
        var s = document.createElement('span').innerText = this.data['timestamp'];
        status.append(s);
        if (this.data['has_local_feedback'] && !this.data['feedback_updated']) {
            var app = this.app;
            var feedback_path = this.data['local_feedback_path'];
            // var url = URLExt.join(this.base_url, 'tree', this.data['local_feedback_path']);
            var link = document.createElement('a');
            link.onclick = function () {
                app.commands.execute('filebrowser:go-to-path', {
                    path: feedback_path
                });
            };
            link.innerText = ' (view feedback)';
            status.append(link);
        }
        else if (this.data['has_exchange_feedback']) {
            var feedback = document.createElement('span');
            feedback.innerText = ' (feedback available to fetch)';
            status.append(feedback);
        }
        else {
            var feedback = document.createElement('span');
            feedback.innerText = '';
            status.append(feedback);
        }
        container.append(status);
        var s1 = document.createElement('span');
        s1.classList.add('item_course', 'col-sm-2');
        container.append(s1);
        var s2 = document.createElement('span');
        s2.classList.add('item_status', 'col-sm-4');
        container.append(s2);
        this.element.append(container);
    }
    ;
}
;
class Notebook {
    constructor(element, data, options, app) {
        this.element = element;
        this.data = data;
        this.options = options;
        this.base_url = options.get('base_url') || _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl();
        this.app = app;
        this.style();
        this.make_row();
    }
    style() {
        this.element.classList.add('list_item', 'row', 'nested_list_item');
    }
    ;
    make_button() {
        var that = this;
        var container = document.createElement('span');
        container.classList.add('item_status', 'col-sm-4');
        var button = document.createElement('button');
        button.classList.add('btn', 'btn-default', 'btn-xs');
        container.append(button);
        button.innerText = 'Validate';
        button.onclick = async function () {
            button.innerText = 'Validating...';
            button.setAttribute('disabled', 'disabled');
            const dataToSend = { path: that.data['path'] };
            try {
                const reply = await requestAPI('assignments/validate', {
                    body: JSON.stringify(dataToSend),
                    method: 'POST'
                });
                button.innerText = 'Validate';
                button.removeAttribute('disabled');
                const success = (0,_common_validate__WEBPACK_IMPORTED_MODULE_4__.validate)(reply);
                if (success)
                    that.validate_success(button);
                else
                    that.validate_failure(button);
            }
            catch (reason) {
                remove_children(container);
                container.innerText = 'Error validating assignment.';
                console.error(`Error on POST /assignments/validate ${dataToSend}.\n${reason}`);
            }
        };
        return container;
    }
    ;
    validate_success(button) {
        button.classList.remove('btn-default', 'btn-danger', 'btn-success');
        button.classList.add('btn-success');
    }
    ;
    validate_failure(button) {
        button.classList.remove('btn-default', 'btn-danger', 'btn-success');
        button.classList.add("btn-danger");
    }
    ;
    make_row() {
        var app = this.app;
        var nb_path = this.data['path'];
        var container = document.createElement('div');
        container.classList.add('col-md-12');
        var s1 = document.createElement('span');
        s1.classList.add('item_name', 'col-sm-6');
        var a = document.createElement('a');
        a.href = '#';
        a.innerText = this.data['notebook_id'];
        a.onclick = function () {
            app.commands.execute('docmanager:open', {
                path: nb_path
            });
        };
        s1.append(a);
        container.append(s1);
        var s2 = document.createElement('span');
        s2.classList.add('item_course', 'col-sm-2');
        container.append(s2);
        container.append(this.make_button());
        this.element.append(container);
    }
    ;
}
;
class CourseList {
    constructor(widget, course_list_selector, default_course_selector, dropdown_selector, refresh_selector, assignment_list, options) {
        this.options = new Map();
        this.course_list_selector = course_list_selector;
        this.default_course_selector = default_course_selector;
        this.dropdown_selector = dropdown_selector;
        this.refresh_selector = refresh_selector;
        this.course_list_element = widget.node.getElementsByTagName('ul').namedItem(course_list_selector);
        var buttons = widget.node.getElementsByTagName('button');
        this.default_course_element = buttons.namedItem(default_course_selector);
        this.dropdown_element = buttons.namedItem(dropdown_selector);
        this.refresh_element = buttons.namedItem(refresh_selector);
        this.assignment_list = assignment_list;
        this.current_course = undefined;
        //options = options || {};
        this.options = options;
        this.base_url = options.get('base_url') || _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getBaseUrl();
        this.data = undefined;
        var that = this;
        /* Open the dropdown course_list when clicking on dropdown toggle button */
        this.dropdown_element.onclick = function () {
            that.course_list_element.classList.toggle('open');
        };
        /* Close the dropdown course_list if clicking anywhere else */
        document.onclick = function (event) {
            if (event.target.closest('button') != that.dropdown_element) {
                that.course_list_element.classList.remove('open');
            }
        };
        this.refresh_element.onclick = function () {
            that.load_list();
        };
        this.bind_events();
    }
    enable_list() {
        this.dropdown_element.removeAttribute("disabled");
    }
    ;
    disable_list() {
        this.dropdown_element.setAttribute("disabled", "disabled");
    }
    ;
    clear_list() {
        // remove list items
        if (this.course_list_element.children.length > 0) {
            this.course_list_element.innerHTML = '';
        }
    }
    ;
    bind_events() {
        this.refresh_element.click();
    }
    ;
    async load_list() {
        this.disable_list();
        this.clear_list();
        this.assignment_list.clear_list(true);
        try {
            const data = await requestAPI('courses');
            this.handle_load_list(data);
        }
        catch (reason) {
            console.error(`Error on GET /courses.\n${reason}`);
        }
    }
    ;
    handle_load_list(data) {
        if (data.success) {
            this.load_list_success(data.value);
        }
        else {
            this.default_course_element.innerText = "Error fetching courses!";
            this.enable_list();
            this.assignment_list.show_error(data.value);
        }
    }
    ;
    load_list_success(data) {
        this.data = data;
        this.disable_list();
        this.clear_list();
        if (this.data.length === 0) {
            this.default_course_element.innerText = "No courses found.";
            this.assignment_list.clear_list(false);
            this.enable_list();
            return;
        }
        if (!this.data.includes(this.current_course)) {
            this.current_course = undefined;
        }
        if (this.current_course === undefined) {
            this.change_course(this.data[0]);
        }
        else {
            // we still want to "change" the course here to update the
            // assignment list
            this.change_course(this.current_course);
        }
    }
    ;
    change_course(course) {
        this.disable_list();
        if (this.current_course !== undefined) {
            this.default_course_element.innerText = course;
        }
        this.current_course = course;
        this.default_course_element.innerText = this.current_course;
        var success = () => { this.load_assignment_list_success(); };
        this.assignment_list.load_list(course, success);
    }
    ;
    load_assignment_list_success() {
        if (this.data) {
            var that = this;
            var set_course = function (course) {
                return function () { that.change_course(course); };
            };
            for (var i = 0; i < this.data.length; i++) {
                var a = document.createElement('a');
                a.href = '#';
                a.innerText = this.data[i];
                var element = document.createElement('li');
                element.append(a);
                element.onclick = set_course(this.data[i]);
                this.course_list_element.append(element);
            }
            this.data = undefined;
        }
        this.enable_list();
    }
    ;
}
/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 
    // 'assignment_list', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    const data = await response.json();
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message);
    }
    return data;
}


/***/ }),

/***/ "./lib/assignment_list/index.js":
/*!**************************************!*\
  !*** ./lib/assignment_list/index.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "assignment_list_extension": () => (/* binding */ assignment_list_extension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _assignmentlist__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./assignmentlist */ "./lib/assignment_list/assignmentlist.js");





const PLUGIN_ID = 'nbgrader/assignment-list';
const COMMAND_NAME = "nbgrader:open-assignment-list";
class AssignmentListWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__.Widget {
    constructor(app) {
        super();
        this.app = app;
        console.log('Initializing the assignments list widget');
        var assignment_html = ([
            '<div id="assignments" class="tab-pane">',
            '  <div id="assignments_toolbar" class="row list_toolbar">',
            '    <div class="col-sm-8 no-padding">',
            '      <span id="assignments_list_info" class="toolbar_info">Released, downloaded, and submitted assignments for course:</span>',
            '      <div class="btn-group btn-group-xs">',
            '        <button type="button" class="btn btn-default" id="course_list_default">Loading, please wait...</button>',
            '        <button type="button" class="btn btn-default dropdown-toggle" id="course_list_dropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" disabled="disabled">',
            '          <span class="caret"></span>',
            '          <span class="sr-only">Toggle Dropdown</span>',
            '        </button>',
            '        <ul class="dropdown-menu" id="course_list">',
            '        </ul>',
            '      </div>',
            '    </div>',
            '    <div class="col-sm-4 no-padding tree-buttons">',
            '      <span id="assignments_buttons" class="pull-right toolbar_buttons">',
            '      <button id="refresh_assignments_list" title="Refresh assignments list" class="btn btn-default btn-xs"><i class="fa fa-refresh"></i></button>',
            '      </span>',
            '    </div>',
            '  </div>',
            '  <div class="alert alert-danger version_error">',
            '  </div>',
            '  <div class="panel-group">',
            '    <div class="panel panel-default">',
            '      <div class="panel-heading">',
            '        Released assignments',
            '      </div>',
            '      <div class="panel-body">',
            '        <div id="released_assignments_list" class="list_container">',
            '          <div id="released_assignments_list_placeholder" class="list_placeholder">',
            '            <div> There are no assignments to fetch. </div>',
            '          </div>',
            '          <div id="released_assignments_list_loading" class="list_loading">',
            '            <div> Loading, please wait... </div>',
            '          </div>',
            '          <div id="released_assignments_list_error" class="list_error">',
            '            <div></div>',
            '          </div>',
            '        </div>',
            '      </div>',
            '    </div>',
            '    <div class="panel panel-default">',
            '      <div class="panel-heading">',
            '        Downloaded assignments',
            '      </div>',
            '      <div class="panel-body">',
            '        <div id="fetched_assignments_list" class="list_container" role="tablist" aria-multiselectable="true">',
            '          <div id="fetched_assignments_list_placeholder" class="list_placeholder">',
            '            <div> There are no downloaded assignments. </div>',
            '          </div>',
            '          <div id="fetched_assignments_list_loading" class="list_loading">',
            '            <div> Loading, please wait... </div>',
            '          </div>',
            '          <div id="fetched_assignments_list_error" class="list_error">',
            '            <div></div>',
            '          </div>',
            '        </div>',
            '      </div>',
            '    </div>',
            '    <div class="panel panel-default">',
            '      <div class="panel-heading">',
            '        Submitted assignments',
            '      </div>',
            '      <div class="panel-body">',
            '        <div id="submitted_assignments_list" class="list_container">',
            '          <div id="submitted_assignments_list_placeholder" class="list_placeholder">',
            '            <div> There are no submitted assignments. </div>',
            '          </div>',
            '          <div id="submitted_assignments_list_loading" class="list_loading">',
            '            <div> Loading, please wait... </div>',
            '          </div>',
            '          <div id="submitted_assignments_list_error" class="list_error">',
            '            <div></div>',
            '          </div>',
            '        </div>',
            '      </div>',
            '    </div>',
            '  </div>   ',
            '</div>'
        ].join('\n'));
        this.node.innerHTML = assignment_html;
        this.node.style.overflowY = 'auto';
        let base_url = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__.PageConfig.getBaseUrl();
        let options = new Map();
        options.set('base_url', base_url);
        var assignment_l = new _assignmentlist__WEBPACK_IMPORTED_MODULE_4__.AssignmentList(this, 'released_assignments_list', 'fetched_assignments_list', 'submitted_assignments_list', options, this.app);
        new _assignmentlist__WEBPACK_IMPORTED_MODULE_4__.CourseList(this, 'course_list', 'course_list_default', 'course_list_dropdown', 'refresh_assignments_list', assignment_l, options);
        this.checkNbGraderVersion();
    }
    checkNbGraderVersion() {
        var warning = this.node.getElementsByClassName('version_error')[0];
        warning.hidden = false;
        (0,_assignmentlist__WEBPACK_IMPORTED_MODULE_4__.requestAPI)('nbgrader_version?version=' + "0.8.0.dev0")
            .then(response => {
            if (!response['success']) {
                warning.innerText = response['message'];
                warning.style.display = 'block';
            }
        })
            .catch(reason => {
            console.error(`Error on GET /assignment_list/nbgrader_version.\n${reason}`);
        });
    }
}
const assignment_list_extension = {
    id: PLUGIN_ID,
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ICommandPalette],
    optional: [_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer],
    activate: async (app, palette, restorer) => {
        // Declare a widget variable
        let widget;
        // Add an application command
        const command = COMMAND_NAME;
        // Track the widget state
        let tracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.WidgetTracker({
            namespace: 'nbgrader-assignment-list'
        });
        app.commands.addCommand(command, {
            label: 'Assignment List',
            execute: () => {
                if (!widget) {
                    const content = new AssignmentListWidget(app);
                    widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.MainAreaWidget({ content });
                    widget.id = 'nbgrader-assignment-list';
                    widget.addClass('nbgrader-mainarea-widget');
                    widget.title.label = 'Assignments';
                    widget.title.closable = true;
                }
                if (!tracker.has(widget)) {
                    // Track the state of the widget for later restoration
                    tracker.add(widget);
                }
                if (!widget.isAttached) {
                    // Attach the widget to the mainwork area if it's not there
                    app.shell.add(widget, 'main');
                }
                widget.content.update();
                // Activate the widget
                app.shell.activateById(widget.id);
            }
        });
        // Add the command to the palette
        palette.addItem({ command, category: 'nbgrader' });
        // Restore the widget state
        if (restorer != null) {
            restorer.restore(tracker, {
                command,
                name: () => 'nbgrader-assignment-list'
            });
        }
        console.log('JupyterLab extension assignment-list is activated!');
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (assignment_list_extension);


/***/ }),

/***/ "./lib/common/validate.js":
/*!********************************!*\
  !*** ./lib/common/validate.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "showNbGraderDialog": () => (/* binding */ showNbGraderDialog),
/* harmony export */   "validate": () => (/* binding */ validate)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_1__);


const CSS_ERROR_DIALOG = 'nbgrader-ErrorDialog';
const CSS_SUCCESS_DIALOG = 'nbgrader-SuccessDialog';
function showNbGraderDialog(options = {}, error = false) {
    const dialog = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog(options);
    if (error)
        dialog.addClass(CSS_ERROR_DIALOG);
    else
        dialog.addClass(CSS_SUCCESS_DIALOG);
    return dialog.launch();
}
function validate(data) {
    var body = document.createElement('div');
    body.id = 'validation-message';
    var isError = false;
    var success = false;
    if (data.success === true) {
        if (typeof (data.value) === "string") {
            data = JSON.parse(data.value);
        }
        else {
            data = data.value;
        }
        if (data.type_changed !== undefined) {
            isError = true;
            for (let i = 0; i < data.type_changed.length; i++) {
                var div = document.createElement('div');
                var paragraph = document.createElement('p');
                paragraph.innerText = `The following ${data.type_changed[i].old_type} cell has changed to a ${data.type_changed[i].new_type} cell, but it should not have!`;
                div.append(paragraph);
                body.append(div);
                var pre = document.createElement('pre');
                pre.innerText = data.type_changed[i].source;
                body.append(pre);
            }
            body.classList.add("validation-type-changed");
        }
        else if (data.changed !== undefined) {
            isError = true;
            for (var i = 0; i < data.changed.length; i++) {
                var div = document.createElement('div');
                var paragraph = document.createElement('p');
                paragraph.innerText = 'The source of the following cell has changed, but it should not have!';
                div.append(paragraph);
                body.append(div);
                var pre = document.createElement('pre');
                pre.innerText = data.changed[i].source;
                body.append(pre);
            }
            body.classList.add("validation-changed");
        }
        else if (data.passed !== undefined) {
            for (var i = 0; i < data.changed.length; i++) {
                var div = document.createElement('div');
                var paragraph = document.createElement('p');
                paragraph.innerText = 'The following cell passed:';
                div.append(paragraph);
                body.append(div);
                var pre = document.createElement('pre');
                pre.innerText = data.passed[i].source;
                body.append(pre);
            }
            body.classList.add("validation-passed");
        }
        else if (data.failed !== undefined) {
            isError = true;
            for (var i = 0; i < data.failed.length; i++) {
                var div = document.createElement('div');
                var paragraph = document.createElement('p');
                paragraph.innerText = 'The following cell failed:';
                div.append(paragraph);
                body.append(div);
                const source = document.createElement('div');
                source.classList.add('jp-RenderedText');
                var pre1 = document.createElement('pre');
                pre1.innerText = data.failed[i].source;
                source.append(pre1);
                body.append(source);
                const error = document.createElement('div');
                error.classList.add('jp-RenderedText');
                var pre2 = document.createElement('pre');
                pre2.innerHTML = data.failed[i].error;
                error.append(pre2);
                body.append(error);
            }
            body.classList.add('validation-failed');
        }
        else {
            var div = document.createElement('div');
            var paragraph = document.createElement('p');
            paragraph.innerText = 'Success! Your notebook passes all the tests.';
            div.append(paragraph);
            body.append(div);
            body.classList.add("validation-success");
            success = true;
        }
    }
    else {
        isError = true;
        var div = document.createElement('div');
        var paragraph = document.createElement('p');
        paragraph.innerText = 'There was an error running the validate command:';
        div.append(paragraph);
        body.append(div);
        var pre = document.createElement('pre');
        pre.innerText = data.value;
        body.append(pre);
    }
    let b;
    b = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__.Widget({ node: body });
    showNbGraderDialog({
        title: "Validation Results",
        body: b,
        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton()]
    }, isError);
    return success;
}
;


/***/ }),

/***/ "./lib/course_list/courselist.js":
/*!***************************************!*\
  !*** ./lib/course_list/courselist.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "CourseList": () => (/* binding */ CourseList),
/* harmony export */   "requestAPI": () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 
    // 'course_list', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    const data = await response.json();
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message);
    }
    return data;
}
function createElementFromCourse(data, app) {
    var element = document.createElement('div');
    element.classList.add('list_item', 'row');
    var row = document.createElement('div');
    row.classList.add('col-md-12');
    var container = document.createElement('span');
    container.classList.add('item_name', 'col-sm-2');
    var anchor = document.createElement('a');
    anchor.href = '#';
    anchor.innerText = data['course_id'];
    if (data['kind'] == 'local') {
        anchor.href = '#';
        anchor.onclick = function () {
            app.commands.execute('nbgrader:open-formgrader', data);
        };
    }
    else {
        const url = data['url'];
        anchor.href = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(url.replace(/formgrader$/, 'lab'), 'workspaces', 'formgrader');
        anchor.target = 'blank';
    }
    var fgkind = document.createElement('span');
    fgkind.classList.add('item_course', 'col-sm-2');
    fgkind.textContent = data['kind'];
    container.append(anchor);
    row.append(container);
    row.append(fgkind);
    element.append(row);
    return element;
}
class CourseList {
    constructor(course_list_element, app) {
        this.course_list_element = course_list_element;
        this.app = app;
        this.listplaceholder = document.createElement('div');
        this.listplaceholder.id = 'formgrader_list_placeholder';
        this.listplaceholder.classList.add('list_placeholder');
        var listplaceholdertext = document.createElement('div');
        listplaceholdertext.textContent = 'There are no available formgrader services.';
        this.listplaceholder.hidden = true;
        this.listplaceholder.appendChild(listplaceholdertext);
        this.course_list_element.appendChild(this.listplaceholder);
        this.listloading = document.createElement('div');
        this.listloading.id = 'formgrader_list_loading';
        this.listloading.classList.add('list_loading');
        var listloadingtext = document.createElement('div');
        listloadingtext.textContent = 'Loading, please wait...';
        this.listloading.appendChild(listloadingtext);
        this.course_list_element.appendChild(this.listloading);
        this.listerror = document.createElement('div');
        this.listerror.id = 'formgrader_list_error';
        this.listerror.classList.add('list_error');
        this.listerrortext = document.createElement('div');
        this.listerrortext.textContent = 'There are no available formgrader services.';
        this.listerror.hidden = true;
        this.listerror.appendChild(this.listerrortext);
        this.course_list_element.appendChild(this.listerror);
    }
    clear_list(loading) {
        while (this.course_list_element.lastChild.classList.contains('list_item')) {
            this.course_list_element.removeChild(this.course_list_element.lastChild);
        }
        if (loading) {
            // show loading
            this.listloading.hidden = false;
            // hide placeholders and errors
            this.listplaceholder.hidden = true;
            this.listerror.hidden = true;
        }
        else {
            // show placeholders
            this.listplaceholder.hidden = false;
            // hide loading and errors
            this.listloading.hidden = true;
            this.listerror.hidden = true;
        }
    }
    show_error(error) {
        while (this.course_list_element.lastChild.classList.contains('list_item')) {
            this.course_list_element.removeChild(this.course_list_element.lastChild);
        }
        // show errors
        this.listerrortext.textContent = error.message;
        this.listerror.hidden = false;
        // hide loading and placeholding
        this.listloading.hidden = true;
        this.listplaceholder.hidden = true;
    }
    load_list() {
        this.clear_list(true);
        requestAPI('formgraders')
            .then((data) => this.handle_load_list.call(this, data))
            .catch(this.show_error);
    }
    handle_load_list(data) {
        if (data.success) {
            this.load_list_success(data.value);
        }
        else {
            this.show_error(data.value);
        }
    }
    load_list_success(data) {
        this.clear_list(false);
        var len = data.length;
        if (len > 0) {
            this.listplaceholder.hidden = true;
        }
        for (var i = 0; i < len; i++) {
            this.course_list_element.appendChild(createElementFromCourse(data[i], this.app));
        }
    }
}


/***/ }),

/***/ "./lib/course_list/index.js":
/*!**********************************!*\
  !*** ./lib/course_list/index.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "course_list_extension": () => (/* binding */ course_list_extension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _courselist__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./courselist */ "./lib/course_list/courselist.js");




const PLUGIN_ID = "nbgrader/course-list";
const COMMAND_NAME = "nbgrader:open-course-list";
class CourseListWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__.Widget {
    constructor(app) {
        super();
        this.app = app;
        var maindiv = document.createElement('div');
        maindiv.id = 'courses';
        maindiv.classList.add("tab-pane");
        this.version_alert = document.createElement('div');
        this.version_alert.classList.add('alert', 'alert-danger', 'version_error');
        this.version_alert.hidden = true;
        maindiv.appendChild(this.version_alert);
        var panelgroup = document.createElement('div');
        panelgroup.classList.add('panel-group');
        var panel = document.createElement('div');
        panel.classList.add('panel', 'panel-default');
        var panelheading = document.createElement('div');
        panelheading.classList.add('panel-heading');
        panelheading.textContent = 'Available formgraders';
        var formgraderbuttons = document.createElement('span');
        formgraderbuttons.id = 'formgrader_buttons';
        formgraderbuttons.classList.add('pull-right', 'toolbar_buttons');
        var refreshbutton = document.createElement('button');
        refreshbutton.id = 'refresh_formgrader_list';
        refreshbutton.title = 'Refresh formgrader list';
        refreshbutton.classList.add('btn', 'btn-default', 'btn-xs');
        // I have no idea why this is an italics tag, but I'm just recreating it so :/
        var buttonimg = document.createElement('i');
        buttonimg.classList.add('fa', 'fa-refresh');
        refreshbutton.appendChild(buttonimg);
        formgraderbuttons.appendChild(refreshbutton);
        panelheading.appendChild(formgraderbuttons);
        panel.appendChild(panelheading);
        var panelbody = document.createElement('div');
        panelbody.classList.add('panel-body');
        var formgraderlist = document.createElement('div');
        formgraderlist.id = 'formgrader_list';
        formgraderlist.classList.add('list_container');
        // further initialization of formgraderlist is in here
        this.courselist = new _courselist__WEBPACK_IMPORTED_MODULE_3__.CourseList(formgraderlist, this.app);
        panelbody.appendChild(formgraderlist);
        panel.appendChild(panelbody);
        panelgroup.appendChild(panel);
        maindiv.appendChild(panelgroup);
        this.node.appendChild(maindiv);
        this.node.style.overflowY = 'auto';
        refreshbutton.onclick = () => this.courselist.load_list.call(this.courselist);
        this.checkNbGraderVersion();
        this.courselist.load_list();
    }
    checkNbGraderVersion() {
        let nbgrader_version = '0.8.0.dev0';
        (0,_courselist__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('nbgrader_version?version=' + nbgrader_version)
            .then(response => {
            if (!response['success']) {
                this.version_alert.textContent = response['message'];
                this.version_alert.hidden = false;
            }
        })
            .catch(reason => {
            console.error(`The course_list server extension appears to be missing.\n${reason}`);
        });
    }
}
/**
 * Initialization data for the course_list extension.
 */
const course_list_extension = {
    id: PLUGIN_ID,
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ICommandPalette],
    optional: [_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer],
    activate: async (app, palette, restorer) => {
        let widget;
        const command = COMMAND_NAME;
        // Track the widget state
        let tracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.WidgetTracker({
            namespace: 'nbgrader-course-list'
        });
        app.commands.addCommand(command, {
            label: 'Course List',
            execute: () => {
                if (!widget) {
                    const content = new CourseListWidget(app);
                    widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.MainAreaWidget({ content });
                    widget.id = 'nbgrader-course-list';
                    widget.addClass('nbgrader-mainarea-widget');
                    widget.title.label = 'Courses';
                    widget.title.closable = true;
                }
                if (!tracker.has(widget)) {
                    tracker.add(widget);
                }
                if (!widget.isAttached) {
                    app.shell.add(widget, 'main');
                }
                widget.content.update();
                app.shell.activateById(widget.id);
            }
        });
        palette.addItem({ command, category: "nbgrader" });
        // Restore the widget state
        if (restorer != null) {
            restorer.restore(tracker, {
                command,
                name: () => 'nbgrader-course-list'
            });
        }
        console.log('JupyterLab extension course-list is activated!');
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (course_list_extension);


/***/ }),

/***/ "./lib/create_assignment/create_assignment_extension.js":
/*!**************************************************************!*\
  !*** ./lib/create_assignment/create_assignment_extension.js ***!
  \**************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "CreateAssignmentWidget": () => (/* binding */ CreateAssignmentWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/algorithm */ "webpack/sharing/consume/default/@lumino/algorithm");
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_algorithm__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./create_assignment_model */ "./lib/create_assignment/create_assignment_model.js");






const CSS_CELL_HEADER = 'nbgrader-CellHeader';
const CSS_CELL_ID = 'nbgrader-CellId';
const CSS_CELL_POINTS = 'nbgrader-CellPoints';
const CSS_CELL_TYPE = 'nbgrader-CellType';
const CSS_CELL_WIDGET = 'nbgrader-CellWidget';
const CSS_CREATE_ASSIGNMENT_WIDGET = 'nbgrader-CreateAssignmentWidget';
const CSS_LOCK_BUTTON = 'nbgrader-LockButton';
const CSS_MOD_ACTIVE = 'nbgrader-mod-active';
const CSS_MOD_HIGHLIGHT = 'nbgrader-mod-highlight';
const CSS_MOD_LOCKED = 'nbgrader-mod-locked';
const CSS_MOD_UNEDITABLE = 'nbgrader-mod-uneditable';
const CSS_NOTEBOOK_HEADER_WIDGET = 'nbgrader-NotebookHeaderWidget';
const CSS_NOTEBOOK_PANEL_WIDGET = 'nbgrader-NotebookPanelWidget';
const CSS_NOTEBOOK_POINTS = 'nbgrader-NotebookPoints';
const CSS_NOTEBOOK_WIDGET = 'nbgrader-NotebookWidget';
const CSS_TOTAL_POINTS_INPUT = 'nbgrader-TotalPointsInput';
const CSS_ERROR_DIALOG = 'nbgrader-ErrorDialog';
function showErrorDialog(options = {}) {
    const dialog = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog(options);
    dialog.addClass(CSS_ERROR_DIALOG);
    return dialog.launch();
}
/**
 * A widget which shows the "Create Assignment" widgets for the active notebook.
 */
class CreateAssignmentWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Panel {
    constructor(tracker, shell) {
        super();
        this.notebookPanelWidgets = new Map();
        this.addClass(CSS_CREATE_ASSIGNMENT_WIDGET);
        this.addNotebookListeners(tracker);
        this.addMainAreaActiveListener(shell);
        this.activeNotebook = null;
        this.notebookTracker = tracker;
        this.shell = shell;
    }
    addNotebookListeners(tracker) {
        this.currentNotebookListener = this.getCurrentNotebookListener();
        tracker.currentChanged.connect(this.currentNotebookListener);
    }
    addMainAreaActiveListener(shell) {
        this.mainAreaListener = this.getMainAreaActiveListener();
        shell.currentChanged.connect(this.mainAreaListener);
    }
    async addNotebookWidget(tracker, panel) {
        if (panel === null)
            return;
        await panel.revealed;
        const notebookPanelWidget = new NotebookPanelWidget(panel);
        this.addWidget(notebookPanelWidget);
        this.notebookPanelWidgets.set(panel, notebookPanelWidget);
        panel.disposed.connect(() => {
            notebookPanelWidget.dispose();
        });
        notebookPanelWidget.disposed.connect(() => {
            this.notebookPanelWidgets.delete(panel);
        });
        if (tracker.currentWidget != panel) {
            notebookPanelWidget.hide();
        }
        return panel.revealed;
    }
    dispose() {
        if (this.isDisposed) {
            return;
        }
        if (this.notebookPanelWidgets != null) {
            for (const widget of this.notebookPanelWidgets) {
                widget[1].dispose();
            }
        }
        if (this.notebookTracker != null) {
            this.removeNotebookListeners(this.notebookTracker);
        }
        this.activeNotebook = null;
        this.notebookPanelWidgets = null;
        this.notebookTracker = null;
        super.dispose();
    }
    getCurrentNotebookListener() {
        return async (tracker, panel) => {
            if (this.activeNotebook != null) {
                const widget = this.notebookPanelWidgets.get(this.activeNotebook);
                if (widget != null) {
                    widget.hide();
                }
            }
            if (panel != null) {
                if (this.isVisible && this.notebookPanelWidgets.get(panel) == null) {
                    await this.addNotebookWidget(tracker, panel);
                }
                const widget = this.notebookPanelWidgets.get(panel);
                if (widget != null) {
                    widget.show();
                }
            }
            this.activeNotebook = panel;
        };
    }
    /*
     * The listener on the main area tab change
     * to collapse create_assignment widget if the current tab is not a Notebook
     */
    getMainAreaActiveListener() {
        return async (shell, changed) => {
            if (!(changed.newValue instanceof _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.NotebookPanel) && this.isVisible) {
                this.hideRightPanel();
            }
        };
    }
    onBeforeShow(msg) {
        super.onBeforeShow(msg);
        if (this.activeNotebook != null) {
            const notebookWidget = this.notebookPanelWidgets.get(this.activeNotebook);
            if (notebookWidget == null) {
                this.addNotebookWidget(this.notebookTracker, this.activeNotebook);
            }
            else {
                notebookWidget.show();
            }
        }
    }
    /*
     * Check if the widget must be visible :
     *  -> is there an active Notebook visible in main panel ?
     */
    onAfterShow() {
        const widgets = this.shell.widgets('main');
        if (this.activeNotebook == null) {
            this.hideRightPanel();
        }
        else {
            (0,_lumino_algorithm__WEBPACK_IMPORTED_MODULE_2__.each)(widgets, w => {
                if (w.title == this.activeNotebook.title) {
                    if (!w.isVisible)
                        this.hideRightPanel();
                    else
                        w.activate();
                }
            });
        }
    }
    hideRightPanel() {
        this.shell.collapseRight();
    }
    removeNotebookListeners(tracker) {
        tracker.currentChanged.disconnect(this.currentNotebookListener);
        this.currentNotebookListener = null;
    }
}
/**
 * Shows a cell's assignment data.
 */
class CellWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Panel {
    constructor(cell) {
        super();
        this._click = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_3__.Signal(this);
        this._cell = cell;
        this.addMetadataListener(cell);
        this.initLayout();
        this.initClickListener();
        this.initInputListeners();
        this.initMetadata(cell);
        this.addClass(CSS_CELL_WIDGET);
    }
    async addMetadataListener(cell) {
        await cell.ready;
        this.metadataChangedHandler = this.getMetadataChangedHandler();
        cell.model.metadata.changed.connect(this.metadataChangedHandler);
    }
    /**
     * The notebook cell associated with this widget.
     */
    get cell() {
        return this._cell;
    }
    cleanNbgraderData(cell) {
        _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.cleanNbgraderData(cell.model.metadata, cell.model.type);
    }
    /**
     * A signal for when this widget receives a click event.
     */
    get click() {
        return this._click;
    }
    dispose() {
        var _a, _b, _c, _d, _e;
        if (this.isDisposed) {
            return;
        }
        if (this.metadataChangedHandler != null) {
            (_d = (_c = (_b = (_a = this.cell) === null || _a === void 0 ? void 0 : _a.model) === null || _b === void 0 ? void 0 : _b.metadata) === null || _c === void 0 ? void 0 : _c.changed) === null || _d === void 0 ? void 0 : _d.disconnect(this.metadataChangedHandler);
        }
        if (this.onclick != null) {
            (_e = this.node) === null || _e === void 0 ? void 0 : _e.removeEventListener('click', this.onclick);
        }
        if (this.taskInput != null) {
            this.taskInput.onchange = null;
        }
        if (this.gradeIdInput != null) {
            this.gradeIdInput.onchange = null;
        }
        if (this.pointsInput != null) {
            this.pointsInput.onchange = null;
        }
        this._cell = null;
        this._click = null;
        this.metadataChangedHandler = null;
        this.onclick = null;
        this.lock = null;
        this.gradeId = null;
        this.points = null;
        this.taskInput = null;
        this.gradeIdInput = null;
        this.pointsInput = null;
        super.dispose();
    }
    getCellStateChangedListener(srcPrompt, destPrompt) {
        return (model, changedArgs) => {
            if (changedArgs.name == 'executionCount') {
                destPrompt.innerText = srcPrompt.innerText;
            }
        };
    }
    getMetadataChangedHandler() {
        return (metadata, changedArgs) => {
            const nbgraderData = _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.getNbgraderData(metadata);
            const toolData = _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.newToolData(nbgraderData, this.cell.model.type);
            this.updateValues(toolData);
        };
    }
    getOnInputChanged() {
        return () => {
            const toolData = new _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.ToolData();
            toolData.type = this.taskInput.value;
            if (!this.gradeId.classList.contains(CSS_MOD_UNEDITABLE)) {
                toolData.id = this.gradeIdInput.value;
            }
            else {
                const nbgraderData = _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.getNbgraderData(this.cell.model.metadata);
                if ((nbgraderData === null || nbgraderData === void 0 ? void 0 : nbgraderData.grade_id) == null) {
                    toolData.id = 'cell-' + this.randomString(16);
                }
                else {
                    toolData.id = nbgraderData.grade_id;
                }
                this.gradeIdInput.value = toolData.id;
            }
            if (!this.points.classList.contains(CSS_MOD_UNEDITABLE)) {
                toolData.points = this.pointsInput.valueAsNumber;
            }
            const data = _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.newNbgraderData(toolData);
            _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.setNbgraderData(data, this.cell.model.metadata);
        };
    }
    getOnTaskInputChanged() {
        const onInputChanged = this.getOnInputChanged();
        return () => {
            onInputChanged();
            this.updateDisplayClass();
        };
    }
    initClickListener() {
        this.onclick = () => {
            this._click.emit();
        };
        this.node.addEventListener('click', this.onclick);
    }
    initInputListeners() {
        this.taskInput.onchange = this.getOnTaskInputChanged();
        this.gradeIdInput.onchange = this.getOnInputChanged();
        this.pointsInput.onchange = this.getOnInputChanged();
    }
    initLayout() {
        const bodyElement = document.createElement('div');
        const headerElement = this.newHeaderElement();
        const taskElement = this.newTaskElement();
        const idElement = this.newIdElement();
        const pointsElement = this.newPointsElement();
        const elements = [headerElement, taskElement, idElement, pointsElement];
        const fragment = document.createDocumentFragment();
        for (const element of elements) {
            fragment.appendChild(element);
        }
        bodyElement.appendChild(fragment);
        this.node.appendChild(bodyElement);
        this.lock = headerElement.getElementsByTagName('a')[0];
        this.gradeId = idElement;
        this.points = pointsElement;
        this.taskInput = taskElement.getElementsByTagName('select')[0];
        this.gradeIdInput = idElement.getElementsByTagName('input')[0];
        this.pointsInput = pointsElement.getElementsByTagName('input')[0];
    }
    async initMetadata(cell) {
        await cell.ready;
        if (cell.model == null) {
            return;
        }
        this.cleanNbgraderData(cell);
        const nbgraderData = _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.getNbgraderData(cell.model.metadata);
        const toolData = _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.newToolData(nbgraderData, this.cell.model.type);
        _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.clearCellType(cell.model.metadata);
        this.updateDisplayClass();
        this.updateValues(toolData);
    }
    newHeaderElement() {
        const element = document.createElement('div');
        element.className = CSS_CELL_HEADER;
        const promptNode = this.cell.promptNode.cloneNode(true);
        element.appendChild(promptNode);
        this.cell.model.stateChanged.connect(this.getCellStateChangedListener(this.cell.promptNode, promptNode));
        const lockElement = document.createElement('a');
        lockElement.className = CSS_LOCK_BUTTON;
        const listElement = document.createElement('li');
        listElement.className = 'fa fa-lock';
        listElement.title = 'Student changes will be overwritten';
        lockElement.appendChild(listElement);
        element.appendChild(lockElement);
        return element;
    }
    newIdElement() {
        const element = document.createElement('div');
        element.className = CSS_CELL_ID;
        const label = document.createElement('label');
        label.textContent = 'ID: ';
        const input = document.createElement('input');
        input.type = 'text';
        label.appendChild(input);
        element.appendChild(label);
        return element;
    }
    newPointsElement() {
        const element = document.createElement('div');
        element.className = CSS_CELL_POINTS;
        const label = document.createElement('label');
        label.textContent = 'Points: ';
        const input = document.createElement('input');
        input.type = 'number';
        input.min = '0';
        label.appendChild(input);
        element.appendChild(label);
        return element;
    }
    newTaskElement() {
        const element = document.createElement('div');
        element.className = CSS_CELL_TYPE;
        const label = document.createElement('label');
        label.textContent = 'Type: ';
        const select = document.createElement('select');
        const options = new Map([
            ['', '-'],
            ['manual', 'Manually graded answer'],
            ['task', 'Manually graded task'],
            ['solution', 'Autograded answer'],
            ['tests', 'Autograded tests'],
            ['readonly', 'Read-only']
        ]);
        if (this.cell.model.type !== 'code') {
            options.delete('solution');
            options.delete('tests');
        }
        const fragment = document.createDocumentFragment();
        for (const optionEntry of options.entries()) {
            const option = document.createElement('option');
            option.value = optionEntry[0];
            option.innerHTML = optionEntry[1];
            fragment.appendChild(option);
        }
        select.appendChild(fragment);
        const selectWrap = _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Styling.wrapSelect(select);
        label.appendChild(selectWrap);
        element.appendChild(label);
        return element;
    }
    randomString(length) {
        var result = '';
        var chars = 'abcdef0123456789';
        var i;
        for (i = 0; i < length; i++) {
            result += chars[Math.floor(Math.random() * chars.length)];
        }
        return result;
    }
    /**
     * Sets this cell as active/focused.
     */
    setActive(active) {
        if (active) {
            this.addClass(CSS_MOD_ACTIVE);
        }
        else {
            this.removeClass(CSS_MOD_ACTIVE);
        }
    }
    setGradeId(value) {
        this.gradeIdInput.value = value;
    }
    setElementEditable(element, visible) {
        if (visible) {
            element.classList.remove(CSS_MOD_UNEDITABLE);
        }
        else {
            element.classList.add(CSS_MOD_UNEDITABLE);
        }
    }
    setGradeIdEditable(visible) {
        this.setElementEditable(this.gradeId, visible);
    }
    setPoints(value) {
        this.pointsInput.value = value.toString();
    }
    setPointsEditable(visible) {
        this.setElementEditable(this.points, visible);
    }
    setTask(value) {
        this.taskInput.value = value;
    }
    updateDisplayClass() {
        const data = _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.getNbgraderData(this.cell.model.metadata);
        if (_create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.isRelevantToNbgrader(data)) {
            this.addClass(CSS_MOD_HIGHLIGHT);
        }
        else {
            this.removeClass(CSS_MOD_HIGHLIGHT);
        }
    }
    updateValues(data) {
        this.setTask(data.type);
        if (data.id == null) {
            this.setGradeIdEditable(false);
            this.setGradeId('');
        }
        else {
            this.setGradeId(data.id);
            this.setGradeIdEditable(true);
        }
        if (data.points == null) {
            this.setPointsEditable(false);
            this.setPoints(0);
        }
        else {
            this.setPoints(data.points);
            this.setPointsEditable(true);
        }
        if (data.locked) {
            this.lock.classList.add(CSS_MOD_LOCKED);
        }
        else {
            this.lock.classList.remove(CSS_MOD_LOCKED);
        }
    }
}
/**
 * The header of a notebook's Create Assignment widget.
 *
 * Displays the total points in the notebook.
 */
class NotebookHeaderWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Widget {
    constructor() {
        super();
        this.addClass(CSS_NOTEBOOK_HEADER_WIDGET);
        this.initLayout();
    }
    dispose() {
        if (this.isDisposed) {
            return;
        }
        this.pointsInput = null;
        super.dispose();
    }
    initLayout() {
        const totalPoints = this.newTotalPointsElement();
        this.node.appendChild(totalPoints);
        this.pointsInput = totalPoints.getElementsByTagName('input')[0];
    }
    newTotalPointsElement() {
        const element = document.createElement('div');
        element.className = CSS_NOTEBOOK_POINTS;
        const label = document.createElement('label');
        label.innerText = 'Total points:';
        const input = document.createElement('input');
        input.className = CSS_TOTAL_POINTS_INPUT;
        input.type = 'number';
        input.disabled = true;
        label.appendChild(input);
        element.appendChild(label);
        return element;
    }
    /**
     * The total points in the notebook.
     */
    set totalPoints(points) {
        if (this.pointsInput != null) {
            this.pointsInput.value = points.toString();
        }
    }
}
/**
 * Contains a list of {@link CellWidget}s for a notebook.
 */
class NotebookWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Panel {
    constructor(panel) {
        super();
        this.activeCell = null;
        this._cellMetadataChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_3__.Signal(this);
        this.cellWidgets = new Map();
        this.metadataChangedHandlers = new Map();
        this.activeCell = panel.content.activeCell;
        this.activeCellWidgetListener = this.getActiveCellWidgetListener();
        this._notebookPanel = panel;
        this.addClass(CSS_NOTEBOOK_WIDGET);
        this.addCellListener(panel);
        this.addCellListListener(panel);
        this.initCellWidgets(panel.content);
        this.validateSchemaVersion();
        this.addValidateIdsListener();
        this.addNotebookDisposedListener(panel);
    }
    addCellListener(panel) {
        this.cellListener = this.getActiveCellListener();
        panel.content.activeCellChanged.connect(this.cellListener);
    }
    addCellListListener(panel) {
        this.cellListListener =
            (sender, args) => {
                switch (args.type) {
                    case 'add': {
                        const cell = this.findCellInArray(args.newValues[0], panel.content.widgets);
                        this.addCellWidget(cell, args.newIndex);
                        break;
                    }
                    case 'move': {
                        const cell = panel.content.widgets[args.newIndex];
                        this.moveCellWidget(cell, args.newIndex);
                        break;
                    }
                    case 'remove': {
                        const cell = this.findDeadCell(this.cellWidgets.keys());
                        if (cell != null) {
                            this.removeCellWidget(cell);
                        }
                        else {
                            console.warn('nbgrader: Unable to find newly deleted cell.');
                        }
                        break;
                    }
                    case 'set': {
                        // Existing notebook cell changed. Update the corresponding widget.
                        const oldCell = this.findDeadCell(this.cellWidgets.keys());
                        if (oldCell != null) {
                            const newCell = this.findCellInArray(args.newValues[0], panel.content.widgets);
                            this.cellWidgets.get(oldCell).dispose();
                            this.cellWidgets.delete(oldCell);
                            const cellWidget = this.addCellWidget(newCell, args.newIndex);
                            if (this.activeCell === newCell) {
                                cellWidget.setActive(this.activeCell === newCell);
                                this.scrollIntoViewNearest(cellWidget);
                            }
                        }
                    }
                }
            };
        panel.model.cells.changed.connect(this.cellListListener);
    }
    addCellWidget(cell, index = undefined) {
        const cellWidget = new CellWidget(cell);
        this.cellWidgets.set(cell, cellWidget);
        if (index == null) {
            this.addWidget(cellWidget);
        }
        else {
            this.insertWidget(index, cellWidget);
        }
        cellWidget.click.connect(this.activeCellWidgetListener);
        const metadataChangedHandler = this.getMetadataChangedHandler(cellWidget);
        cell.model.metadata.changed.connect(metadataChangedHandler);
        this.metadataChangedHandlers.set(cellWidget, metadataChangedHandler);
        return cellWidget;
    }
    addNotebookDisposedListener(panel) {
        this.notebookDisposedListener = this.getNotebookDisposedListener();
        panel.disposed.connect(this.notebookDisposedListener);
    }
    addValidateIdsListener() {
        this.validateIdsListener =
            (context, args) => {
                if (args != 'started') {
                    return;
                }
                this.validateIds();
            };
        this.notebookPanel.context.saveState.connect(this.validateIdsListener);
    }
    /**
     * A signal which is evoked when one of the cell's metadata changes.
     */
    get cellMetadataChanged() {
        return this._cellMetadataChanged;
    }
    dispose() {
        var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k, _l, _m, _o;
        if (this.isDisposed) {
            return;
        }
        if (this.cellWidgets != null) {
            for (const widgets of this.cellWidgets) {
                this.removeCellWidget(widgets[0]);
            }
        }
        if (this.cellListener != null) {
            (_c = (_b = (_a = this.notebookPanel) === null || _a === void 0 ? void 0 : _a.content) === null || _b === void 0 ? void 0 : _b.activeCellChanged) === null || _c === void 0 ? void 0 : _c.disconnect(this.cellListener);
        }
        if (this.cellListListener != null) {
            (_g = (_f = (_e = (_d = this.notebookPanel) === null || _d === void 0 ? void 0 : _d.model) === null || _e === void 0 ? void 0 : _e.cells) === null || _f === void 0 ? void 0 : _f.changed) === null || _g === void 0 ? void 0 : _g.disconnect(this.cellListListener);
        }
        if (this.validateIdsListener != null) {
            (_k = (_j = (_h = this.notebookPanel) === null || _h === void 0 ? void 0 : _h.context) === null || _j === void 0 ? void 0 : _j.saveState) === null || _k === void 0 ? void 0 : _k.disconnect(this.validateIdsListener);
        }
        if (this.notebookDisposedListener != null) {
            (_m = (_l = this.notebookPanel) === null || _l === void 0 ? void 0 : _l.disposed) === null || _m === void 0 ? void 0 : _m.disconnect(this.notebookDisposedListener);
        }
        (_o = this.notebookPanel) === null || _o === void 0 ? void 0 : _o.dispose();
        this.activeCell = null;
        this.activeCellWidgetListener = null;
        this.cellListener = null;
        this.cellListListener = null;
        this._cellMetadataChanged = null;
        this.cellWidgets = null;
        this.metadataChangedHandlers = null;
        this.notebookDisposedListener = null;
        this._notebookPanel = null;
        this.validateIdsListener = null;
        super.dispose();
    }
    findCellInArray(model, cells) {
        return cells.find((value, index, obj) => {
            return value.model === model;
        });
    }
    findDeadCell(cells) {
        for (const cell of cells) {
            if (cell.model == null) {
                return cell;
            }
        }
        return undefined;
    }
    getActiveCellListener() {
        return (notebook, cell) => {
            if (this.activeCell != null) {
                const activeWidget = this.cellWidgets.get(this.activeCell);
                if (activeWidget != null) {
                    activeWidget.setActive(false);
                }
            }
            if (cell != null) {
                const activeWidget = this.cellWidgets.get(cell);
                if (activeWidget != null) {
                    activeWidget.setActive(true);
                    this.scrollIntoViewNearest(activeWidget);
                }
            }
            this.activeCell = cell;
        };
    }
    getActiveCellWidgetListener() {
        return (cellWidget) => {
            const i = this.notebookPanel.content.widgets.indexOf(cellWidget.cell);
            this.notebookPanel.content.activeCellIndex = i;
        };
    }
    getNotebookDisposedListener() {
        return (panel) => {
            this.dispose();
        };
    }
    initCellWidgets(notebook) {
        for (const cell of notebook.widgets) {
            const cellWidget = this.addCellWidget(cell);
            cellWidget.setActive(notebook.activeCell === cell);
        }
    }
    getMetadataChangedHandler(cellWidget) {
        return (metadata, args) => {
            this.cellMetadataChanged.emit(cellWidget);
        };
    }
    moveCellWidget(cell, index) {
        const cellWidget = this.cellWidgets.get(cell);
        this.insertWidget(index, cellWidget);
    }
    /**
     * The notebook panel associated with this widget.
     */
    get notebookPanel() {
        return this._notebookPanel;
    }
    removeCellWidget(cell) {
        var _a, _b, _c, _d, _e;
        if (this.cellWidgets == null) {
            return;
        }
        const cellWidget = this.cellWidgets.get(cell);
        if (cellWidget == null) {
            return;
        }
        if (this.activeCellWidgetListener != null) {
            (_a = cellWidget.click) === null || _a === void 0 ? void 0 : _a.disconnect(this.activeCellWidgetListener);
        }
        const handler = (_b = this.metadataChangedHandlers) === null || _b === void 0 ? void 0 : _b.get(cellWidget);
        if (handler != null) {
            (_e = (_d = (_c = cell.model) === null || _c === void 0 ? void 0 : _c.metadata) === null || _d === void 0 ? void 0 : _d.changed) === null || _e === void 0 ? void 0 : _e.disconnect(handler);
        }
        this.cellWidgets.delete(cell);
        cellWidget.dispose();
    }
    validateIds() {
        const set = new Set();
        const valid = /^[a-zA-Z0-9_\-]+$/;
        const iter = this.notebookPanel.model.cells.iter();
        for (let cellModel = iter.next(); cellModel != null; cellModel = iter.next()) {
            const data = _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.getNbgraderData(cellModel.metadata);
            if (data == null)
                continue;
            const id = data.grade_id;
            if (!valid.test(id)) {
                this.warnInvalidId(true, false, id);
                return;
            }
            else if (set.has(id)) {
                this.warnInvalidId(false, true, id);
                return;
            }
            else {
                set.add(id);
            }
        }
    }
    validateSchemaVersion() {
        const iter = this.notebookPanel.model.cells.iter();
        for (let cellModel = iter.next(); cellModel != null; cellModel = iter.next()) {
            const data = _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.getNbgraderData(cellModel.metadata);
            let version = data == null ? null : data.schema_version;
            version = version === undefined ? 0 : version;
            if (version != null && version < _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.NBGRADER_SCHEMA_VERSION) {
                this.warnSchemaVersion(version);
                return;
            }
        }
    }
    warnInvalidId(badFormat, duplicateId, id) {
        const options = {
            buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton()],
            title: undefined,
            body: undefined
        };
        if (badFormat) {
            options.title = 'Invalid nbgrader cell ID';
            options.body = 'At least one cell has an invalid nbgrader ID. Cell IDs ' +
                'must contain at least one character, and may only contain ' +
                'letters, numbers, hyphens, and/or underscores.';
            showErrorDialog(options);
            return;
        }
        else if (duplicateId) {
            options.title = 'Duplicate nbgrader cell ID';
            options.body = `The nbgrader ID "${id}" has been used for more than ` +
                `one cell. Please make sure all grade cells have unique ids.`;
            showErrorDialog(options);
            return;
        }
    }
    warnSchemaVersion(schemaVersion) {
        const version = schemaVersion.toString();
        const notebookPath = this.notebookPanel.sessionContext.path;
        const body = document.createElement('p');
        const code = document.createElement('code');
        const bodyWidget = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Widget({ node: body });
        const options = {
            title: 'Outdated schema version',
            body: bodyWidget,
            buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton()]
        };
        body.innerText =
            `At least one cell has an old version (${version}) of the ` +
                'nbgrader metadata. Please back up this notebook and then ' +
                'update the metadata on the command ' +
                'line using the following command: ';
        code.innerText = `nbgrader update ${notebookPath}`;
        body.appendChild(code);
        showErrorDialog(options);
    }
    scrollIntoViewNearest(widget) {
        const parentTop = this.node.scrollTop;
        const parentBottom = parentTop + this.node.clientHeight;
        const widgetTop = widget.node.offsetTop;
        const widgetBottom = widgetTop + widget.node.clientHeight;
        if (widgetTop < parentTop) {
            widget.node.scrollIntoView(true);
        }
        else if (widgetBottom > parentBottom) {
            if (widgetBottom - widgetTop > parentBottom - parentTop) {
                widget.node.scrollIntoView(true);
            }
            else {
                widget.node.scrollIntoView(false);
            }
        }
    }
}
/**
 * Contains a notebook's "Create Assignment" UI.
 */
class NotebookPanelWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Panel {
    constructor(panel) {
        super();
        this.addClass(CSS_NOTEBOOK_PANEL_WIDGET);
        this.initLayout(panel);
        this.setUpTotalPoints();
    }
    calcTotalPoints() {
        let totalPoints = 0;
        const iter = this.notebookWidget.notebookPanel.model.cells.iter();
        for (let cellModel = iter.next(); cellModel != null; cellModel = iter.next()) {
            const data = _create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.getNbgraderData(cellModel.metadata);
            const points = (data == null || data.points == null
                || !_create_assignment_model__WEBPACK_IMPORTED_MODULE_5__.CellModel.isGraded(data)) ? 0 : data.points;
            totalPoints += points;
        }
        return totalPoints;
    }
    dispose() {
        var _a, _b, _c, _d, _e, _f, _g, _h, _j;
        if (this.isDisposed) {
            return;
        }
        if (this.cellListListener != null) {
            (_e = (_d = (_c = (_b = (_a = this.notebookWidget) === null || _a === void 0 ? void 0 : _a.notebookPanel) === null || _b === void 0 ? void 0 : _b.model) === null || _c === void 0 ? void 0 : _c.cells) === null || _d === void 0 ? void 0 : _d.changed) === null || _e === void 0 ? void 0 : _e.disconnect(this.cellListListener);
        }
        if (this.cellModelListener != null) {
            (_g = (_f = this.notebookWidget) === null || _f === void 0 ? void 0 : _f.cellMetadataChanged) === null || _g === void 0 ? void 0 : _g.disconnect(this.cellModelListener);
        }
        (_h = this.notebookHeaderWidget) === null || _h === void 0 ? void 0 : _h.dispose();
        (_j = this.notebookWidget) === null || _j === void 0 ? void 0 : _j.dispose();
        this.cellListListener = null;
        this.cellModelListener = null;
        this.notebookHeaderWidget = null;
        this.notebookWidget = null;
        super.dispose();
    }
    initLayout(panel) {
        this.notebookHeaderWidget = new NotebookHeaderWidget();
        this.notebookWidget = new NotebookWidget(panel);
        this.addWidget(this.notebookHeaderWidget);
        this.addWidget(this.notebookWidget);
    }
    setUpTotalPoints() {
        this.notebookHeaderWidget.totalPoints = this.calcTotalPoints();
        this.cellListListener =
            (cellModels, args) => {
                if (args.type != 'move') {
                    this.notebookHeaderWidget.totalPoints = this.calcTotalPoints();
                }
            };
        this.cellModelListener =
            (notebookWidget, cellWidget) => {
                this.notebookHeaderWidget.totalPoints = this.calcTotalPoints();
            };
        this.notebookWidget.notebookPanel.model.cells.changed.connect(this.cellListListener);
        this.notebookWidget.cellMetadataChanged.connect(this.cellModelListener);
    }
}


/***/ }),

/***/ "./lib/create_assignment/create_assignment_model.js":
/*!**********************************************************!*\
  !*** ./lib/create_assignment/create_assignment_model.js ***!
  \**********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "CellModel": () => (/* binding */ CellModel),
/* harmony export */   "NBGRADER_SCHEMA_VERSION": () => (/* binding */ NBGRADER_SCHEMA_VERSION),
/* harmony export */   "NbgraderData": () => (/* binding */ NbgraderData),
/* harmony export */   "ToolData": () => (/* binding */ ToolData)
/* harmony export */ });
const NBGRADER_KEY = 'nbgrader';
const NBGRADER_SCHEMA_VERSION = 3;
/**
 * A namespace for conversions between {@link NbgraderData} and
 * {@link ToolData} and for reading and writing to notebook cells' metadata.
 */
var CellModel;
(function (CellModel) {
    /**
     * Cleans invalid nbgrader data if necessary.
     *
     * @returns Whether cleaning occurred.
     */
    function cleanNbgraderData(cellMetadata, cellType) {
        const data = CellModel.getNbgraderData(cellMetadata);
        if (data == null || !PrivateNbgraderData.isInvalid(data, cellType)) {
            return false;
        }
        data.schema_version = NBGRADER_SCHEMA_VERSION;
        data.solution = false;
        data.grade = false;
        data.locked = false;
        data.task = false;
        CellModel.setNbgraderData(data, cellMetadata);
        return true;
    }
    CellModel.cleanNbgraderData = cleanNbgraderData;
    /**
     * Removes the "cell_type" property from the nbgrader data.
     */
    function clearCellType(cellMetadata) {
        const data = cellMetadata.get(NBGRADER_KEY);
        if (data == null) {
            return;
        }
        if ('cell_type' in data) {
            data['cell_type'] = undefined;
        }
        cellMetadata.set(NBGRADER_KEY, data);
    }
    CellModel.clearCellType = clearCellType;
    /**
     * Read the nbgrader data from a cell's metadata.
     *
     * @returns The nbgrader data, or null if it doesn't exist.
     */
    function getNbgraderData(cellMetadata) {
        if (cellMetadata == null) {
            return null;
        }
        const nbgraderValue = cellMetadata.get('nbgrader');
        if (nbgraderValue == null) {
            return null;
        }
        return nbgraderValue.valueOf();
    }
    CellModel.getNbgraderData = getNbgraderData;
    /**
     * @returns True if the cell is gradable.
     */
    function isGraded(data) {
        return PrivateNbgraderData.isGraded(data);
    }
    CellModel.isGraded = isGraded;
    /**
     * @returns True if the cell relevant to nbgrader. A cell is relevant if it is
     * gradable or contains autograder tests.
     */
    function isRelevantToNbgrader(data) {
        return PrivateNbgraderData.isGraded(data)
            || PrivateNbgraderData.isSolution(data);
    }
    CellModel.isRelevantToNbgrader = isRelevantToNbgrader;
    /**
     * Converts {@link ToolData} to {@link NbgraderData}.
     *
     * @returns The converted data, or null if the nbgrader cell type is not set.
     */
    function newNbgraderData(data) {
        if (data.type === '') {
            return null;
        }
        const nbgraderData = new NbgraderData();
        nbgraderData.grade = PrivateToolData.getGrade(data);
        nbgraderData.grade_id = PrivateToolData.getGradeId(data);
        nbgraderData.locked = PrivateToolData.getLocked(data);
        nbgraderData.points = PrivateToolData.getPoints(data);
        nbgraderData.schema_version = PrivateToolData.getSchemeaVersion();
        nbgraderData.solution = PrivateToolData.getSolution(data);
        nbgraderData.task = PrivateToolData.getTask(data);
        return nbgraderData;
    }
    CellModel.newNbgraderData = newNbgraderData;
    /**
     * Converts {@link NbgraderData} to {@link ToolData}.
     *
     * @param data The data to convert. Can be null.
     * @param cellType The notebook cell widget type.
     */
    function newToolData(data, cellType) {
        const toolData = new ToolData;
        if (PrivateNbgraderData.isInvalid(data, cellType)) {
            toolData.type = '';
            return toolData;
        }
        toolData.type = PrivateNbgraderData.getType(data, cellType);
        if (toolData.type === '') {
            return toolData;
        }
        if (PrivateNbgraderData.isGrade(data)
            || PrivateNbgraderData.isSolution(data)
            || PrivateNbgraderData.isLocked(data)) {
            toolData.id = PrivateNbgraderData.getGradeId(data);
        }
        if (PrivateNbgraderData.isGraded(data)) {
            toolData.points = PrivateNbgraderData.getPoints(data);
        }
        toolData.locked = PrivateNbgraderData.isLocked(data);
        return toolData;
    }
    CellModel.newToolData = newToolData;
    /**
     * Writes the nbgrader data to a cell's metadata.
     *
     * @param data The nbgrader data. If null, the nbgrader entry, if it exists,
     * will be removed from the metadata.
     */
    function setNbgraderData(data, cellMetadata) {
        if (data == null) {
            if (cellMetadata.has(NBGRADER_KEY)) {
                cellMetadata.delete(NBGRADER_KEY);
            }
            return;
        }
        const currentDataJson = cellMetadata.get(NBGRADER_KEY);
        const currentData = currentDataJson == null ? null :
            currentDataJson.valueOf();
        if (currentData != data) {
            cellMetadata.set(NBGRADER_KEY, data.toJson());
        }
    }
    CellModel.setNbgraderData = setNbgraderData;
})(CellModel || (CellModel = {}));
var PrivateNbgraderData;
(function (PrivateNbgraderData) {
    function getGradeId(nbgraderData) {
        if (nbgraderData == null || nbgraderData.grade_id == null) {
            return '';
        }
        return nbgraderData.grade_id;
    }
    PrivateNbgraderData.getGradeId = getGradeId;
    function getPoints(nbgraderData) {
        if (nbgraderData == null) {
            return 0;
        }
        return PrivateNbgraderData._to_float(nbgraderData.points);
    }
    PrivateNbgraderData.getPoints = getPoints;
    function getSchemeaVersion(nbgraderData) {
        if (nbgraderData === null) {
            return 0;
        }
        return nbgraderData.schema_version;
    }
    PrivateNbgraderData.getSchemeaVersion = getSchemeaVersion;
    function getType(nbgraderData, cellType) {
        if (PrivateNbgraderData.isTask(nbgraderData)) {
            return 'task';
        }
        else if (PrivateNbgraderData.isSolution(nbgraderData)
            && isGrade(nbgraderData)) {
            return 'manual';
        }
        else if (PrivateNbgraderData.isSolution(nbgraderData)
            && cellType === 'code') {
            return 'solution';
        }
        else if (PrivateNbgraderData.isGrade(nbgraderData)
            && cellType === 'code') {
            return 'tests';
        }
        else if (PrivateNbgraderData.isLocked(nbgraderData)) {
            return 'readonly';
        }
        else {
            return '';
        }
    }
    PrivateNbgraderData.getType = getType;
    function isGrade(nbgraderData) {
        return nbgraderData != null && nbgraderData.grade === true;
    }
    PrivateNbgraderData.isGrade = isGrade;
    function isGraded(nbgraderData) {
        return PrivateNbgraderData.isGrade(nbgraderData)
            || PrivateNbgraderData.isTask(nbgraderData);
    }
    PrivateNbgraderData.isGraded = isGraded;
    function isInvalid(nbgraderData, cellType) {
        return !PrivateNbgraderData.isTask(nbgraderData) && cellType !== 'code'
            && (PrivateNbgraderData.isSolution(nbgraderData)
                != PrivateNbgraderData.isGrade(nbgraderData));
    }
    PrivateNbgraderData.isInvalid = isInvalid;
    function isLocked(nbgraderData) {
        return !PrivateNbgraderData.isSolution(nbgraderData)
            && (PrivateNbgraderData.isGraded(nbgraderData)
                || (nbgraderData != null && nbgraderData.locked === true));
    }
    PrivateNbgraderData.isLocked = isLocked;
    function isSolution(nbgraderData) {
        return nbgraderData != null && nbgraderData.solution === true;
    }
    PrivateNbgraderData.isSolution = isSolution;
    function isTask(nbgraderData) {
        return nbgraderData != null && nbgraderData.task === true;
    }
    PrivateNbgraderData.isTask = isTask;
    function _to_float(val) {
        if (val == null || val === '') {
            return 0;
        }
        const valType = typeof (val);
        if (valType === 'string') {
            return parseFloat(val);
        }
        else if (valType === 'number') {
            return val;
        }
        return 0;
    }
    PrivateNbgraderData._to_float = _to_float;
})(PrivateNbgraderData || (PrivateNbgraderData = {}));
var PrivateToolData;
(function (PrivateToolData) {
    function getGrade(data) {
        return data.type === 'manual' || data.type === 'tests';
    }
    PrivateToolData.getGrade = getGrade;
    function getGradeId(data) {
        return data.id == null ? '' : data.id;
    }
    PrivateToolData.getGradeId = getGradeId;
    function getLocked(data) {
        if (PrivateToolData.getSolution(data)) {
            return false;
        }
        if (PrivateToolData.getGrade(data)) {
            return true;
        }
        return data.type === 'task' || data.type === 'tests'
            || data.type === 'readonly';
    }
    PrivateToolData.getLocked = getLocked;
    function getPoints(data) {
        if (!PrivateToolData.getGrade(data) && !PrivateToolData.getTask(data)) {
            return undefined;
        }
        return data.points >= 0 ? data.points : 0;
    }
    PrivateToolData.getPoints = getPoints;
    function getSchemeaVersion() {
        return NBGRADER_SCHEMA_VERSION;
    }
    PrivateToolData.getSchemeaVersion = getSchemeaVersion;
    function getSolution(data) {
        return data.type === 'manual' || data.type === 'solution';
    }
    PrivateToolData.getSolution = getSolution;
    function getTask(data) {
        return data.type === 'task';
    }
    PrivateToolData.getTask = getTask;
})(PrivateToolData || (PrivateToolData = {}));
/**
 * Dummy class for representing the nbgrader cell metadata.
 */
class NbgraderData {
    toJson() {
        const json = {};
        if (this.grade != null) {
            json['grade'] = this.grade;
        }
        if (this.grade_id != null) {
            json['grade_id'] = this.grade_id;
        }
        if (this.locked != null) {
            json['locked'] = this.locked;
        }
        if (this.points != null) {
            json['points'] = this.points;
        }
        if (this.schema_version != null) {
            json['schema_version'] = this.schema_version;
        }
        if (this.solution != null) {
            json['solution'] = this.solution;
        }
        if (this.task != null) {
            json['task'] = this.task;
        }
        return json;
    }
}
/**
 * Dummy class for representing the UI input/output values.
 */
class ToolData {
}


/***/ }),

/***/ "./lib/create_assignment/index.js":
/*!****************************************!*\
  !*** ./lib/create_assignment/index.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "create_assignment_extension": () => (/* binding */ create_assignment_extension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _create_assignment_extension__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./create_assignment_extension */ "./lib/create_assignment/create_assignment_extension.js");




const PLUGIN_ID = "nbgrader/create-assignment";
/**
 * Initialization data for the create_assignment extension.
 */
const create_assignment_extension = {
    id: PLUGIN_ID,
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.INotebookTracker, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILabShell],
    activate: activate_extension
};
function activate_extension(app, tracker, shell) {
    console.log('Activating extension "create_assignment".');
    const panel = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__.Panel();
    panel.node.style.overflowY = 'auto';
    const createAssignmentWidget = new _create_assignment_extension__WEBPACK_IMPORTED_MODULE_3__.CreateAssignmentWidget(tracker, shell);
    panel.addWidget(createAssignmentWidget);
    panel.id = 'nbgrader-create_assignemnt';
    panel.title.label = 'Create Assignment';
    panel.title.caption = 'nbgrader Create Assignment';
    app.shell.add(panel, 'right');
    console.log('Extension "create_assignment" activated.');
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (create_assignment_extension);


/***/ }),

/***/ "./lib/formgrader/index.js":
/*!*********************************!*\
  !*** ./lib/formgrader/index.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   "formgrader_extension": () => (/* binding */ formgrader_extension)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__);




const PLUGIN_ID = "nbgrader/formgrader";
const COMMAND_NAME = "nbgrader:open-formgrader";
class FormgraderWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.IFrame {
    constructor(app, url) {
        super();
        this.referrerPolicy = 'strict-origin-when-cross-origin';
        this.sandbox = ['allow-scripts', 'allow-same-origin', 'allow-forms'];
        this.node.id = "formgrader-iframe";
        this.app = app;
        this.url = url;
        var this_widget = this;
        window.addEventListener('message', function (event) {
            this_widget.on_click(event);
        });
    }
    on_click(event) {
        var contentWindow = this.node.querySelector('iframe').contentWindow;
        if (contentWindow === event.source) {
            var data = JSON.parse(event.data);
            this.app.commands.execute(data.command, data.arguments);
        }
    }
}
;
/**
 * Initialization data for the formfrader extension.
 */
const formgrader_extension = {
    id: PLUGIN_ID,
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ICommandPalette],
    optional: [_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer],
    activate: async (app, palette, restorer) => {
        console.log('JupyterLab extension formgrader is activated!');
        // Declare a widget variable
        let widget;
        // Add an application command
        const command = COMMAND_NAME;
        // Track the widget state
        let tracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.WidgetTracker({
            namespace: 'nbgrader-formgrader'
        });
        app.commands.addCommand(command, {
            label: 'Formgrader',
            execute: async (args) => {
                if (!widget) {
                    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_2__.ServerConnection.makeSettings();
                    const url = args.url || _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.URLExt.join(settings.baseUrl, "formgrader");
                    const content = new FormgraderWidget(app, url);
                    widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.MainAreaWidget({ content });
                    widget.id = 'formgrader';
                    widget.title.label = 'Formgrader';
                    widget.title.closable = true;
                }
                if (!tracker.has(widget)) {
                    // Track the state of the widget for later restoration
                    tracker.add(widget);
                }
                if (!widget.isAttached) {
                    // Attach the widget to the mainwork area if it's not there
                    app.shell.add(widget, 'main');
                }
                widget.content.update();
                // Activate the widget
                app.shell.activateById(widget.id);
            }
        });
        // Add the command to the palette
        palette.addItem({ command, category: 'nbgrader' });
        // Restore the widget state
        if (restorer != null) {
            restorer.restore(tracker, {
                command,
                name: () => 'nbgrader-formgrader'
            });
        }
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (formgrader_extension);


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _assignment_list_index__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./assignment_list/index */ "./lib/assignment_list/index.js");
/* harmony import */ var _formgrader_index__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./formgrader/index */ "./lib/formgrader/index.js");
/* harmony import */ var _course_list_index__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./course_list/index */ "./lib/course_list/index.js");
/* harmony import */ var _create_assignment_index__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./create_assignment/index */ "./lib/create_assignment/index.js");
/* harmony import */ var _validate_assignment_index__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./validate_assignment/index */ "./lib/validate_assignment/index.js");





/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ([_formgrader_index__WEBPACK_IMPORTED_MODULE_0__.formgrader_extension, _assignment_list_index__WEBPACK_IMPORTED_MODULE_1__.assignment_list_extension, _course_list_index__WEBPACK_IMPORTED_MODULE_2__.course_list_extension, _create_assignment_index__WEBPACK_IMPORTED_MODULE_3__.create_assignment_extension, _validate_assignment_index__WEBPACK_IMPORTED_MODULE_4__.validate_assignment_extension]);


/***/ }),

/***/ "./lib/validate_assignment/index.js":
/*!******************************************!*\
  !*** ./lib/validate_assignment/index.js ***!
  \******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ButtonExtension": () => (/* binding */ ButtonExtension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   "validate_assignment_extension": () => (/* binding */ validate_assignment_extension)
/* harmony export */ });
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _validateassignment__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./validateassignment */ "./lib/validate_assignment/validateassignment.js");
/* harmony import */ var _common_validate__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../common/validate */ "./lib/common/validate.js");




var nbgrader_version = "0.8.0.dev0"; // TODO: hardcoded value
const PLUGIN_ID = "nbgrader/validate-assignment";
class ValidateButton extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton {
    constructor(panel) {
        super({
            className: 'validate-button',
            // iconClass: 'fa fa-fast-forward',
            label: 'Validate',
            onClick: () => { this.buttonCallback(); },
            tooltip: 'Validate Assignment'
        });
        this._buttonCallback = this.newButtonCallback();
        this._versionCheckCallback = this.newVersionCheckCallback();
        this._saveCallback = this.newSaveCallback();
        this.panel = panel;
    }
    get buttonCallback() {
        return this._buttonCallback;
    }
    get saveCallback() {
        return this._saveCallback;
    }
    get versionCheckCallback() {
        return this._versionCheckCallback;
    }
    dispose() {
        if (this.isDisposed) {
            return;
        }
        this.panel = null;
        super.dispose();
    }
    newSaveCallback() {
        return (sender, args) => {
            if (args !== 'completed' && args !== 'failed') {
                return;
            }
            this.panel.context.saveState.disconnect(this.saveCallback);
            if (args !== "completed") {
                (0,_common_validate__WEBPACK_IMPORTED_MODULE_2__.showNbGraderDialog)({
                    title: "Validation failed",
                    body: "Cannot save notebook",
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton()],
                    focusNodeSelector: 'input'
                }, true);
                this.setButtonLabel();
                this.setButtonDisabled(false);
                return;
            }
            this.setButtonLabel('Validating...');
            const notebook_path = this.panel.context.path;
            (0,_validateassignment__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('assignments/validate', { method: 'POST' }, new Map([['path', notebook_path]])).then(data => {
                (0,_common_validate__WEBPACK_IMPORTED_MODULE_2__.validate)(data);
                this.setButtonLabel();
                this.setButtonDisabled(false);
            }).catch(reason => {
                (0,_common_validate__WEBPACK_IMPORTED_MODULE_2__.showNbGraderDialog)({
                    title: "Validation failed",
                    body: `Cannot validate: ${reason}`,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton()],
                    focusNodeSelector: 'input'
                }, true);
                this.setButtonLabel();
                this.setButtonDisabled(false);
            });
        };
    }
    newVersionCheckCallback() {
        return (data) => {
            if (data.success !== true) {
                (0,_common_validate__WEBPACK_IMPORTED_MODULE_2__.showNbGraderDialog)({
                    title: "Version Mismatch",
                    body: data.message,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton()],
                    focusNodeSelector: 'input'
                }, true);
                return;
            }
            // tests/test-docregistry/src/context.spec.ts:98
            this.setButtonDisabled();
            this.setButtonLabel('Saving...');
            this.panel.context.saveState.connect(this.saveCallback);
            // examples/notebook/src/commands.ts:79
            this.panel.context.save();
        };
    }
    newButtonCallback() {
        return () => {
            (0,_validateassignment__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('nbgrader_version', undefined, new Map([['version', nbgrader_version]])).then(this.versionCheckCallback).catch(reason => {
                // The validate_assignment server extension appears to be missing
                (0,_common_validate__WEBPACK_IMPORTED_MODULE_2__.showNbGraderDialog)({
                    title: "Validation failed",
                    body: `Cannot check version: ${reason}`,
                    buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton()],
                    focusNodeSelector: 'input'
                }, true);
            });
        };
    }
    setButtonDisabled(disabled = true) {
        const button = this.node.getElementsByTagName('button')[0];
        if (disabled) {
            button.setAttribute('disabled', 'disabled');
        }
        else {
            button.removeAttribute('disabled');
        }
    }
    setButtonLabel(label = 'Validate') {
        const labelElement = this.node.getElementsByClassName('jp-ToolbarButtonComponent-label')[0];
        labelElement.innerText = label;
    }
}
class ButtonExtension {
    /**
     * Create a new extension object.
     */
    createNew(panel, context) {
        const button = new ValidateButton(panel);
        let children = panel.toolbar.children();
        let index = 0;
        for (let i = 0;; i++) {
            let widget = children.next();
            if (widget == undefined) {
                break;
            }
            if (widget.node.classList.contains("jp-Toolbar-spacer")) {
                index = i;
                break;
            }
        }
        panel.toolbar.insertItem(index, 'runAll', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_0__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
/**
 * Initialization data for the validate_assignment extension.
 */
const validate_assignment_extension = {
    id: PLUGIN_ID,
    autoStart: true,
    activate: (app) => {
        console.log('JupyterLab extension validate-assignment is activated!');
        app.docRegistry.addWidgetExtension('Notebook', new ButtonExtension());
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (validate_assignment_extension);


/***/ }),

/***/ "./lib/validate_assignment/validateassignment.js":
/*!*******************************************************!*\
  !*** ./lib/validate_assignment/validateassignment.js ***!
  \*******************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "requestAPI": () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}, params = undefined) {
    const searchParams = new URLSearchParams();
    if (params != null) {
        for (const entry of params.entries()) {
            searchParams.append(entry[0], entry[1]);
        }
    }
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, endPoint) + '?' + searchParams.toString();
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    const data = await response.json();
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message);
    }
    return data;
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.e13fa3930d8707c3421a.js.map