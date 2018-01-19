define(['knockout', 'text!./navigation-bar.html', 'graphql', 'hasher'], function (ko, template, graphql, hasher) {
    'use strict';

    function ViewModel(params) {
        this.projects = ko.observable([]);
        this.route = params.route;

        this.currentProject = ko.computed(() => {
            var projectId = this.route().projectId;
            if (projectId) {
                var project = this.projects().find(project => project.id === projectId);
                if (project) {
                    return {
                        id: project.id,
                        name: project.name,
                        screenshotsUrl: `projects/${project.id}/screenshots`,
                        stringsUrl: `projects/${project.id}/strings`,
                        translationsUrl: `projects/${project.id}/translations`
                    }
                }
            }
        });

        graphql({
            query: `
                query {
                    projects {
                        id
                        name
                    }
                }
            `
        }).then(response => {
            var projects = response.data.projects;
            this.projects(projects);
        });
    };

    return { template, viewModel: ViewModel }
});
