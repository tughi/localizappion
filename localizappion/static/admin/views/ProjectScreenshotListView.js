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

        <div id="uploader" class="card">
            <div class="card-body">
                Drop screenshots here to upload.
                <% if (uploads.length) { %>
                    <div class="busy"></div>
                <% } %>
            </div>
        </div>

        <% if (project.screenshots.length) { %>
            <p>
            <div class="d-flex justify-content-center flex-wrap">
                <% _.each(project.screenshots, screenshot => { %>
                    <a href="#projects/<%= project.id %>/screenshots/<%= screenshot.id %>" class="m-2 screenshot <% if (screenshot.strings.length == 0) { %>without-strings<% } %>">
                        <img src="<%= screenshot.url %>" />
                        <% _.each(screenshot.strings, string => {
                            area = string.area.match('\\\\(([0-9.]+),([0-9.]+)\\\\)x\\\\(([0-9.]+),([0-9.]+)\\\\)');
                            %>
                            <div class="area hidden-on-hover" style="left: <%= area[1] %>%; top: <%= area[2] %>%; right: <%= 100 - area[3] %>%; bottom: <%= 100 - area[4] %>%;"></div>
                        <% }) %>
                    </a>
                <% }) %>
            </div>
            </p>
        <% } %>
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
                            id
                            url
                            strings {
                                area
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
                                            id
                                            url
                                            strings {
                                                area
                                            }
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
