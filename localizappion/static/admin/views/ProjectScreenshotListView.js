Localizappion.ProjectScreenshotListView = Localizappion.ProjectBaseView.extend({
    id: 'project-screenshot-list',

    template: _.template(`
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="#projects">Projects</a></li>
                <li class="breadcrumb-item"><a href="#projects/<%= project.id %>"><%= project.name %></a></li>
                <li class="breadcrumb-item active" aria-current="page">Screenshots</li>
            </ol>
        </nav>

        <% if (project.screenshots.length) { %>
            <div class="row pt-3">
                <% _.each(project.screenshots, screenshot => { %>
                    <div class="col-sm-6 col-md-4 col-lg-3 col-xl-2 pb-3">
                        <div class="card<% if (screenshot.strings.length == 0) { %> text-white bg-warning<% } %>">
                            <img class="card-img" src="<%= screenshot.url %>" />
                            <div class="card-footer">
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
                <% if (uploads.length) { %>
                    <div class="busy"></div>
                <% } %>
            </div>
        </div>
    `),

    events: {
        'dragexit #uploader': 'onDragLeave',
        'dragleave #uploader': 'onDragLeave',
        'dragover #uploader': 'onDragOver',
        'drop #uploader': 'onDrop',
    },

    initialize(projectId) {
        this.initializeProject({
            query: `
                query ($id: ID!) {
                    project(id: $id) {
                        id
                        name
                        screenshots {
                            name
                            url
                            contentLength
                            contentType
                            strings {
                                screenshotArea
                            }
                        }
                    }
                }
            `,
            variables: { id: projectId }
        });

        this.model.set({ uploads: [] });
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
        model.set('uploads', model.get('uploads').concat(_.map(images, image => image.name)));

        for (var i = 0; i < images.length; i++) {
            var image = images[i];

            var reader = new FileReader();
            reader.image = image;
            reader.onload = function(event) {
                var image = this.image;
                $.post(
                    'graphql',
                    {
                        query: `
                            mutation ($projectId: ID!, $name: String!, $content: String!) {
                                createScreenshot(projectId: $projectId, name: $name, content: $content) {
                                    project {
                                        id
                                        name
                                        screenshots {
                                            name
                                            url
                                            contentLength
                                            contentType
                                        }
                                    }
                                }
                            }
                        `,
                        variables: JSON.stringify({
                            projectId: model.get('project').id,
                            name: image.name,
                            content: event.target.result
                        })
                    }
                ).then(response => {
                    if (response.data.createScreenshot) {
                        model.set({
                            project: response.data.createScreenshot.project
                        });
                    }
                }).always(function() {
                    var uploads = [].concat(model.get('uploads'));
                    var uploadIndex = uploads.indexOf(image.name);
                    if (uploadIndex >= 0) {
                        uploads.splice(uploadIndex, 1);
                        model.set('uploads', uploads);
                    }
                });
            };
            reader.readAsDataURL(image);
        }
    }
});
