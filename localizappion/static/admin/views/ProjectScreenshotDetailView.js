Localizappion.ProjectScreenshotDetailView = (function () {
    var AddStringDialog = Backbone.View.extend({
        el: '#add-string-dialog',

        template: _.template(`
            <div class="modal fade" role="dialog">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Add string</h5>
                        </div>
                        <div class="modal-body">
                            <input id="filter" type="text" placeholder="Filter" class="form-control">

                            <div id="list"></div>
                        </div>
                    </div>
                </div>
            </div>
        `),

        listTemplate: _.template(`
            <% if (filter.length > 2) { %>
                <div class="list-group mt-3">
                    <% _.each(strings, string => { %>
                        <% if (string.valueOther.indexOf(filter) >= 0 || string.name.indexOf(filter) >= 0 || (string.valueOne && string.valueOne.indexOf(filter) >= 0)) { %>
                            <div class="list-group-item list-group-item-action">
                                <% if (string.valueOne) { %>
                                    <h5 class="mb-1"><%= string.valueOne %> <span class="text-muted">(One)</span></h5>
                                <% } %>
                                <h5 class="mb-1"><%= string.valueOther %><% if (string.valueOne) { %> <span class="text-muted">(Other)</span><% } %></h5>
                                <small class="text-muted"><%= string.name %></small>
                            </div>
                        <% } %>
                    <% }) %>
                </div>
            <% } %>
        `),

        events: {
            'keyup #filter': 'onFilter'
        },

        initialize() {
            this.model = new Backbone.Model({
                filter: '',
                strings: []
            });

            this.listenTo(this.model, 'change:strings', this.render);
            this.listenTo(this.model, 'change:filter', this.renderList);
        },

        render() {
            this.$el
                .empty()
                .html(this.template(this.model.attributes));

            return this;
        },

        renderList() {
            this.$('#list')
                .empty()
                .html(this.listTemplate(this.model.attributes));

            return this;
        },

        show() {
            this.$('#filter').val('');
            this.model.set({ filter: '' });
            this.$('.modal').modal();
        },

        onFilter(event) {
            this.model.set({ filter: this.$('#filter').val() });
        }
    });

    return Localizappion.ProjectBaseView.extend({
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

            <div id="add-string-dialog"></div>
        `),

        events: {
            'click #add-string': 'onAddString',
            'click #delete-screenshot': 'onDeleteScreenshot',
        },

        initialize(projectId, screenshotId) {
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
                variables: { projectId, screenshotId }
            });

            this.model.once('change:project', model => {
                this.addStringDialog = new AddStringDialog();
                this.addStringDialog.model.set({ strings: model.get('project').strings });
            });
        },

        onAddString() {
            this.addStringDialog.show();
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
})();
