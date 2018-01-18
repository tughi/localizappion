define(['knockout', 'text!./navigation-bar.html', 'graphql', 'hasher'], function (ko, template, graphql, hasher) {
    'use strict';

    function ViewModel(params) {
        this.projects = ko.observable([]);
        this.route = params.route;

        this.currentProject = ko.computed(() => {
            var projectId = this.route().projectId;
            if (projectId) {
                return this.projects().find(project => project.id === projectId);
            }
        });

        this.projects.subscribe(projects => {
            if (!this.currentProject()) {
                hasher.setHash(`projects/${projects.length ? projects[0].id : 'new'}`);
            }
        });

        this.route.subscribe(route => {
            if (!this.currentProject()) {
                var projects = this.projects();
                hasher.setHash(`projects/${projects.length ? projects[0].id : 'new'}`);
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
