Localizappion.ProjectScreenshotDetailView = (function () {
    var AvailableStringsView = Backbone.View.extend({
        id: '#available-strings',

        template: _.template(`
            <% if (addStringFilter.length > 2) { %>
                <div class="list-group mt-3">
                    <% _.each(strings, string => { %>
                        <% if (string.valueOther.indexOf(addStringFilter) >= 0 || (string.valueOne && string.valueOne.indexOf(addStringFilter) >= 0)) { %>
                            <div class="list-group-item list-group-item-action string">
                                <% if (string.valueOne) { %>
                                    <h5 class="mb-1"><%= string.valueOne %> <span class="text-muted">(One)</span></h5>
                                <% } %>
                                <h5 class="mb-1"><%= string.valueOther %><% if (string.valueOne) { %> <span class="text-muted">(Other)</span><% } %></h5>
                                <small class="string-name text-muted"><%= string.name %></small>
                            </div>
                        <% } %>
                    <% }) %>
                </div>
            <% } %>
        `),

        events: {
            'click .string': 'onStringClicked'
        },

        initialize(options) {
            this.listenTo(this.model, 'change:addStringFilter', this.render);
        },

        render() {
            this.$el.html(this.template(this.model.attributes));

            return this;
        },

        onStringClicked(event) {
            var stringName = $(event.target).closest('.string').find('.string-name').text();
            var project = this.model.get('project');
            var string = _.find(this.model.get('strings'), string => string.name === stringName);

            this.model.set({ showAddStringDialog: false });

            graphql({
                query: `
                    mutation ($projectId: ID!, $screenshotId: ID!, $stringId: ID!) {
                        addProjectScreenshotString(projectId: $projectId, screenshotId: $screenshotId, stringId: $stringId) {
                            project {
                                id
                                name
                                screenshot(id: $screenshotId) {
                                    id
                                    name
                                    url
                                    strings {
                                        area
                                        string {
                                            name
                                            valueOne
                                            valueOther
                                        }
                                    }
                                }
                            }
                        }
                    }
                `,
                variables: {
                    projectId: project.id,
                    screenshotId: project.screenshot.id,
                    stringId: string.id
                }
            }).then(response => {
                var project = response.data.addProjectScreenshotString.project;
                if (project) {
                    this.model.set({ project });
                }
            });
        }
    });

    var AddStringDialog = Backbone.View.extend({
        id: 'add-string-dialog',

        template: _.template(`
            <div class="modal fade" role="dialog">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Add string</h5>
                        </div>
                        <div class="modal-body">
                            <input id="filter" type="text" placeholder="Filter" class="form-control">

                            <div id="available-strings"></div>
                        </div>
                    </div>
                </div>
            </div>
        `),

        events: {
            'keyup #filter': 'onFilter',
            'hidden.bs.modal .modal': 'onDialogHidden',
            'shown.bs.modal .modal': 'onDialogShown'
        },

        initialize(options) {
            this.model.set({
                addStringFilter: '',
                strings: []
            });

            this.listenTo(this.model, 'change:showAddStringDialog', this.showAddStringDialog);
        },

        onDialogHidden() {
            this.model.set({ showAddStringDialog: false });
        },

        onDialogShown() {
            this.$('#filter').trigger('focus');
        },

        showAddStringDialog() {
            this.$('.modal').modal(this.model.get('showAddStringDialog') ? 'show' : 'hide');
        },

        render() {
            this.$el.html(this.template(this.model.attributes));

            new AvailableStringsView({
                model: this.model,
                el: this.$('#available-strings')
            });

            return this;
        },

        onFilter(event) {
            this.model.set({ addStringFilter: this.$('#filter').val() });
        }
    });

    var ScreenshotView = Localizappion.ProjectBaseView.extend({
        id: 'project-screenshot-detail',

        template: _.template(`
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="#projects">Projects</a></li>
                    <li class="breadcrumb-item"><a href="#projects/<%= project.id %>"><%= project.name %></a></li>
                    <li class="breadcrumb-item"><a href="#projects/<%= project.id %>/screenshots">Screenshots</a></li>
                    <li class="breadcrumb-item active" aria-current="page"><%= project.screenshot.name %></li>
                </ol>
            </nav>

            <div class="row mb-3">
                <div id="screenshot" class="col-sm-12 col-md-5 col-xl-4">
                    <img src="<%= project.screenshot.url %>" class="mb-3"/>
                    <button id="delete-screenshot" class="btn btn-danger btn-block mb-3">Delete screenshot</button>
                </div>
                <div class="col-sm-12 col-md-7 col-xl-8">
                    <% if (project.screenshot.strings.length) { %>
                        <div class="list-group mb-3">
                            <% _.each(project.screenshot.strings, string => { %>
                                <div class="list-group-item list-group-item-action">
                                    <h5 class="mb-1"><%= string.string.valueOther %></h5>
                                    <small class="text-muted"><%= string.string.name %></small>
                                </div>
                            <% }) %>
                        </div>
                    <% } %>
                    <button id="add-string" class="btn btn-secondary btn-block">Add string</button>
                </div>
            </div>
        `),

        events: {
            'click #add-string': 'onAddStringButtonClicked',
            'click #delete-screenshot': 'onDeleteScreenshot',
        },

        initialize(options) {
            this.initializeProject({
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
            });

            this.model.once('change:project', model => {
                this.model.set({ strings: model.get('project').strings });
            });
        },

        onAddStringButtonClicked() {
            this.model.set({ showAddStringDialog: true });
        },

        onDeleteScreenshot() {
            var project = this.model.get('project');
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
                        screenshotId: project.screenshot.id
                    }
                }).then(response => {
                    if (response.data.deleteProjectScreenshot.ok) {
                        Localizappion.router.navigate(`projects/${project.id}/screenshots`, { trigger: true })
                    }
                });
            }
        }
    });

    return Backbone.View.extend({
        id: 'project-screenshot-detail',

        initialize(projectId, screenshotId) {
            this.screenshotView = new ScreenshotView({ projectId, screenshotId });
            this.addStringDialog = new AddStringDialog({ model: this.screenshotView.model });
        },

        render() {
            this.$el.append(this.screenshotView.render().el);
            this.$el.append(this.addStringDialog.render().el);

            return this;
        }
    });
})();
