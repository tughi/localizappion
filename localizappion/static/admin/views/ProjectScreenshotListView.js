Localizappion.ProjectScreenshotListView = (function() {
    return Backbone.View.extend({
        id: 'project-screenshot-list',

        template: _.template(`
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="#projects">Projects</a></li>
                    <li class="breadcrumb-item"><a href="#projects/<%= project.uuid %>"><%= project.name %></a></li>
                    <li class="breadcrumb-item active" aria-current="page">Screenshots</li>
                </ol>
            </nav>

            <% if (project.screenshots.length) { %>
                <div class="row pt-3">
                    <% _.each(project.screenshots, function (screenshot) { %>
                        <div class="col-sm-6 col-md-4 col-lg-3 col-xl-2 pb-3">
                            <div class="card ">
                                <img class="card-img" src="static/screenshots/device-2018-01-06-213936.png" />
                                <div class="card-footer text-muted">
                                    <%= screenshot.name %>
                                </div>
                            </div>
                        </div>
                    <% }) %>
                </div>
            <% } %>

            <div id="uploader" class="card">
                <div class="card-body">
                    Drop screenshots here to upload.
                </div>
            </div>
        `),

        events: {
            'dragexit #uploader': 'onDragLeave',
            'dragleave #uploader': 'onDragLeave',
            'dragover #uploader': 'onDragOver',
            'drop #uploader': 'onDrop',
        },

        initialize(uuid) {
            var model = this.model = new Backbone.Model({
                uploads: []
            });

            $.post(
                'graphql',
                {
                    query: `
                        query ($uuid: String!) {
                            project(uuid: $uuid) {
                                id
                                uuid
                                name
                                screenshots {
                                    name
                                    contentLength
                                    contentType
                                }
                            }
                        }
                    `,
                    variables: JSON.stringify({
                        uuid: uuid
                    })
                }
            ).then(response => {
                model.set({
                    project: response.data.project
                });
            });

            this.listenTo(model, 'change', this.render);
        },

        render() {
            this.$el.empty();

            if (this.model.has('project')) {
                this.$el.html(this.template(this.model.attributes));
            }

            return this;
        },

        onDragLeave(event) {
            event.preventDefault();

            this.$('#uploader').removeClass('text-white bg-secondary');
        },

        onDragOver(event) {
            event.preventDefault();
            event.originalEvent.dataTransfer.dropEffect = 'copy';
            this.$('#uploader').addClass('text-white bg-secondary');
        },

        onDrop(event) {
            event.preventDefault();
            this.$('#uploader').removeClass('text-white bg-secondary');

            var dataTransfer = event.originalEvent.dataTransfer;
            var images = [];
            if (dataTransfer.items) {
                for (var i = 0; i < dataTransfer.items.length; i++) {
                    var item = dataTransfer.items[i];
                    if (item.kind === 'file') {
                        var file = item.getAsFile();
                        if (file.type.startsWith('image/')) {
                            images.push(file);
                        }
                    }
                }
            } else {
                for (var i = 0; i < dataTransfer.files.length; i++) {
                    var file = dataTransfer.files[i];
                    if (file.type.startsWith('image/')) {
                        images.push(file);
                    }
                }
            }

            var model = this.model;
            for (var i = 0; i < images.length; i++) {
                var image = images[i];

                var reader = new FileReader();
                reader.image = image;
                reader.onload = function(event) {
                    $.post(
                        'graphql',
                        {
                            query: `
                                mutation ($projectId: ID!, $name: String!, $content: String!) {
                                    createScreenshot(projectId: $projectId, name: $name, content: $content) {
                                        project {
                                            id
                                            uuid
                                            name
                                            screenshots {
                                                name
                                                contentLength
                                                contentType
                                            }
                                        }
                                    }
                                }
                            `,
                            variables: JSON.stringify({
                                projectId: model.get('project').id,
                                name: this.image.name,
                                content: event.target.result
                            })
                        }
                    ).then(response => {
                        model.set({
                            project: response.data.createScreenshot.project
                        });
                    });
                };
                reader.readAsDataURL(image);
            }
        }
    });
})();