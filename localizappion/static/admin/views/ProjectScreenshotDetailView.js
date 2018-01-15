Localizappion.ProjectScreenshotDetailView = (function () {
    var Breadcrumb = Backbone.View.extend({
        template: _.template(`
            <% if (project) { %>
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="#projects">Projects</a></li>
                    <li class="breadcrumb-item"><a href="#projects/<%= project.id %>"><%= project.name %></a></li>
                    <li class="breadcrumb-item"><a href="#projects/<%= project.id %>/screenshots">Screenshots</a></li>
                    <li class="breadcrumb-item active" aria-current="page"><%= screenshot.name %></li>
                </ol>
            <% } %>
        `),

        initialize(options) {
            this.listenTo(this.model, 'change:project', this.render);
        },

        render() {
            this.$el.html(this.template(this.model.attributes));
        }
    });

    var ScreenshotAreas = Backbone.View.extend({
        initialize(options) {
            this.listenTo(this.model, 'change:activeScreenshotStringName', this.render);
            this.listenTo(this.model, 'change:pointedScreenshotString', this.render);
            this.listenTo(this.model, 'change:screenshotStrings', this.render);
        },

        events: {
            'mousedown': 'startArea',
            'mousemove': 'updateArea',
            'mouseup': 'finishArea'
        },

        render() {
            this.$el.empty();

            var activeScreenshotStringName = this.model.get('activeScreenshotStringName');
            var screenshotStrings = this.model.get('screenshotStrings');

            _.each(screenshotStrings, screenshotString => {
                var area = screenshotString.area.match(/\(([0-9.]+),([0-9.]+)\)x\(([0-9.]+),([0-9.]+)\)/);

                $('<div class="area" />')
                    .addClass(screenshotString.string.name === activeScreenshotStringName ? 'active' : null)
                    .css({
                        left: area[1] + '%',
                        top: area[2] + '%',
                        right: (100 - area[3]) + '%',
                        bottom: (100 - area[4]) + '%'
                    })
                    .appendTo(this.$el);
            });
        },

        startArea(event) {
            if (this.model.get('activeScreenshotStringName')) {
                event.preventDefault();

                this.drawingStart = {
                    x: event.pageX,
                    y: event.pageY
                };
            }
        },

        updateArea(event) {
            var start = this.drawingStart;
            if (start) {
                event.preventDefault();

                var stop = this.drawingStop = {
                    x: event.pageX,
                    y: event.pageY
                };

                var $area = this.$('.area.active');
                if ($area.length) {
                    var parentOffset = this.$el.offset();

                    $area.css({
                        left: (start.x - parentOffset.left) + 'px',
                        top: (start.y - parentOffset.top) + 'px',
                        width: (stop.x - start.x) + 'px',
                        height: (stop.y - start.y) + 'px',
                        right: 'auto',
                        bottom: 'auto'
                    });
                }
            } else {
                // TODO: draw guides
            }
        },

        finishArea(event) {
            if (this.drawingStart) {
                this.drawingStart = null;

                var $area = this.$('.area.active');
                if ($area.length) {
                    var areaPosition = $area.position();
                    var areaWidth = $area.width();
                    var areaHeight = $area.height();
                    var parentWidth = this.$el.width();
                    var parentHeight = this.$el.height();

                    var x1 = Math.round(areaPosition.left / parentWidth * 10000) / 100;
                    var y1 = Math.round(areaPosition.top / parentHeight * 10000) / 100;
                    var x2 = Math.round((areaPosition.left + areaWidth) / parentWidth * 10000) / 100;
                    var y2 = Math.round((areaPosition.top + areaHeight) / parentHeight * 10000) / 100;

                    var activeScreenshotStringName = this.model.get('activeScreenshotStringName');
                    var activeScreenshotString = _.find(this.model.get('screenshotStrings'), screenshotString => screenshotString.string.name === activeScreenshotStringName);
                    if (activeScreenshotString) {
                        activeScreenshotString.area = `(${x1},${y1})x(${x2},${y2})`;
                        this.model.trigger('change:screenshotStrings');
                    }
                }
            }
        }
    });

    var ScreenshotStrings = Backbone.View.extend({
        template: _.template(`
            <% if (screenshotStrings.length) { %>
                <div class="list-group mb-3">
                    <% _.each(screenshotStrings, screenshotString => { %>
                        <div class="string list-group-item list-group-item-action <%= activeScreenshotStringName === screenshotString.string.name ? 'active' : null %>">
                            <% if (screenshotString.string.valueOne) { %>
                                <h5 class="mb-1">
                                    <%= screenshotString.string.valueOne %>
                                    <span class="text-muted">(One)</span>
                                </h5>
                            <% } %>
                            <h5 class="mb-1">
                                <%= screenshotString.string.valueOther %>
                                <% if (screenshotString.string.valueOne) { %>
                                    <span class="text-muted">(Other)</span>
                                <% } %>
                            </h5>
                            <small class="string-name <%= activeScreenshotStringName === screenshotString.string.name ? null : 'text-muted' %>"><%= screenshotString.string.name %></small>
                        </div>
                    <% }) %>
                </div>
            <% } %>
        `),

        events: {
            'click .string': 'setActiveScreenshotStringName',
            'mouseenter .string': 'setPointedScreenshotString',
            'mouseleave .string': 'unsetPointedScreenshotString',
        },

        initialize(options) {
            this.listenTo(this.model, 'change:activeScreenshotStringName', this.render);
            this.listenTo(this.model, 'change:screenshotStrings', this.render);
        },

        render() {
            this.$el.html(this.template(this.model.attributes));
        },

        setActiveScreenshotStringName(event) {
            var stringName = $(event.target).closest('.string').find('> .string-name').text();
            this.model.set({
                activeScreenshotStringName: stringName
            });
        },

        setPointedScreenshotString(event) {
            var stringName = $(event.target).closest('.string').find('> .string-name').text();
            this.model.set({
                pointedScreenshotString: stringName
            });
        },

        unsetPointedScreenshotString() {
            this.model.set({
                pointedScreenshotString: null
            });
        }
    });

    var AvailableStrings = Backbone.View.extend({
        template: _.template(`
            <% if (availableStringsFilter.length > 2) { %>
                <div class="list-group mt-3">
                    <% _.each(projectStrings, string => { %>
                        <% if (string.valueOther.indexOf(availableStringsFilter) >= 0 || (string.valueOne && string.valueOne.indexOf(availableStringsFilter) >= 0)) { %>
                            <% if (_.find(screenshotStrings, screenshotString => screenshotString.string.name === string.name) == null) { %>
                                <div class="list-group-item list-group-item-action string">
                                    <% if (string.valueOne) { %>
                                        <h5 class="mb-1"><%= string.valueOne %> <span class="text-muted">(One)</span></h5>
                                    <% } %>
                                    <h5 class="mb-1"><%= string.valueOther %><% if (string.valueOne) { %> <span class="text-muted">(Other)</span><% } %></h5>
                                    <small class="string-name text-muted"><%= string.name %></small>
                                </div>
                            <% } %>
                        <% } %>
                    <% }) %>
                </div>
            <% } %>
        `),

        events: {
            'click .string': 'addScreenshotString'
        },

        initialize() {
            this.listenTo(this.model, 'change:availableStringsFilter', this.render);
        },

        render() {
            this.$el.html(this.template(this.model.attributes));
        },

        addScreenshotString(event) {
            var stringName = $(event.target).closest('.string').children('.string-name').text();

            var screenshotStrings = this.model.get('screenshotStrings');
            screenshotStrings.push({
                area: '(0,0)x(0,0)',
                string: _.find(this.model.get('projectStrings'), string => string.name === stringName)
            })

            this.model.set({
                screenshotStrings,
                activeScreenshotStringName: stringName
            });

            $(event.target).closest('.modal').modal('hide');
        }
    });

    return Backbone.View.extend({
        id: 'project-screenshot-detail',

        template: _.template(`
            <nav id="breadcrumb" />

            <div class="row">
                <div class="col-sm-12 col-md-5 col-xl-4 mb-3">
                    <div id="screenshot">
                        <img />
                        <div id="screenshot-areas" />
                    </div>
                </div>
                <div id="screenshot-strings" class="col-sm-12 col-md-7 col-xl-8">
                </div>
            </div>

            <div class="row mb-3">
                <div class="col-12">
                    <div class="card bg-light">
                        <div class="card-body">
                            <button id="delete-screenshot" class="btn btn-danger mr-3">Delete</button>
                            <span class="float-right">
                                <button id="add-string" class="btn btn-secondary mr-1">Add string</button>
                                <button id="save-screenshot" class="btn btn-primary mr-3">Save</button>
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div id="add-string-dialog" class="modal fade" role="dialog">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Add string</h5>
                        </div>
                        <div class="modal-body">
                            <input id="available-strings-filter" type="text" placeholder="Filter" class="form-control">

                            <div id="available-strings"></div>
                        </div>
                    </div>
                </div>
            </div>
        `),

        events: {
            'click #delete-screenshot': 'deleteScreenshot',
            'click #add-string': 'showAddStringDialog',
            'click #save-screenshot': 'saveScreenshot',
            'keyup #available-strings-filter': 'updateAvailableStringsFilter',
            'shown.bs.modal #add-string-dialog': 'focusAddStringFilter',
        },

        initialize(options) {
            this.model = new Backbone.Model({
                project: null,
                projectStrings: null,
                screenshot: null,
                screenshotStrings: null,
                activeScreenshotStringName: null,
                pointedScreenshotString: null,
                availableStringsFilter: ''
            });

            this.listenTo(this.model, 'change:screenshot', model => this.$('#screenshot > img').attr('src', model.get('screenshot').url));

            graphql({
                query: `
                    query ($projectId: ID!, $screenshotId: ID!) {
                        project(id: $projectId) {
                            id
                            name
                            screenshot(id: $screenshotId) {
                                id
                                name
                                url
                                strings {
                                    area
                                    string {
                                        id
                                        name
                                        valueOne
                                        valueOther
                                    }
                                }
                            }
                            strings {
                                id
                                name
                                valueOne
                                valueOther
                            }
                        }
                    }
                `,
                variables: {
                    projectId: options.projectId,
                    screenshotId: options.screenshotId
                }
            }).then(response => {
                var project = response.data.project;
                var projectStrings = project.strings;
                delete project.strings;
                var screenshot = project.screenshot;
                delete project.screenshot;
                var screenshotStrings = screenshot.strings;
                delete screenshot.strings;

                this.model.set({
                    project,
                    projectStrings,
                    screenshot,
                    screenshotStrings
                });
            });
        },

        render() {
            this.$el.html(this.template(this.model.attributes));

            new Breadcrumb({
                el: this.$('nav#breadcrumb')[0],
                model: this.model
            });
            new ScreenshotAreas({
                el: this.$('#screenshot-areas')[0],
                model: this.model
            });
            new ScreenshotStrings({
                el: this.$('#screenshot-strings')[0],
                model: this.model
            });
            new AvailableStrings({
                el: this.$('#available-strings')[0],
                model: this.model
            });

            return this;
        },

        deleteScreenshot() {
            var project = this.model.get('project');
            var screenshot = this.model.get('screenshot');

            // TODO: use bootstrap modal
            if (prompt('Delete screenshot? (yes/no)') === 'yes') {
                graphql({
                    query: `
                        mutation($projectId: ID!, $screenshotId: ID!) {
                            deleteProjectScreenshot(projectId: $projectId, screenshotId: $screenshotId) {
                                ok
                            }
                        }
                    `,
                    variables: {
                        projectId: project.id,
                        screenshotId: screenshot.id
                    }
                }).then(response => {
                    if (response.data.deleteProjectScreenshot.ok) {
                        Localizappion.router.navigate(`projects/${project.id}/screenshots`, { trigger: true })
                    }
                });
            }
        },

        saveScreenshot() {
            this.$('button').attr({ disabled: true });

            var project = this.model.get('project');
            var screenshot = this.model.get('screenshot');
            var screenshotStrings = this.model.get('screenshotStrings');

            graphql({
                query: `
                    mutation($projectId: ID!, $screenshotId: ID!, $screenshotStrings: [ScreenshotStringInputType]!) {
                        updateProjectScreenshotStrings(projectId: $projectId, screenshotId: $screenshotId, screenshotStrings: $screenshotStrings) {
                            screenshot {
                                strings {
                                    area
                                    string {
                                        id
                                        name
                                        valueOne
                                        valueOther
                                    }
                                }
                            }
                        }
                    }
                `,
                variables: {
                    projectId: project.id,
                    screenshotId: screenshot.id,
                    screenshotStrings: _.map(screenshotStrings, screenshotString => {
                        return {
                            area: screenshotString.area,
                            stringId: screenshotString.string.id
                        };
                    })
                }
            }).then(response => {
                this.$('button').attr({ disabled: false });

                this.model.set({
                    screenshotStrings: response.data.updateProjectScreenshotStrings.screenshot.strings,
                    activeScreenshotStringName: null
                });
            });
        },

        showAddStringDialog() {
            this.$('#add-string-dialog').modal('show');
        },

        updateAvailableStringsFilter() {
            this.model.set({
                availableStringsFilter: this.$('#available-strings-filter').val()
            });
        },

        focusAddStringFilter() {
            this.$('#available-strings-filter').trigger('focus');
        }
    });
})();
