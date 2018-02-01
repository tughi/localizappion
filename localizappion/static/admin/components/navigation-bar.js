define(['knockout', 'text!./navigation-bar.html', 'graphql', 'hasher'], function (ko, template, graphql, hasher) {
    'use strict';

    function ViewModel(params) {
        this.projects = params.projects;
        this.activeTab = params.activeTab;

        this.currentProject = ko.computed(() => {
            let projectId = ko.unwrap(params.projectId);
            return this.projects().find(project => project.id === projectId);
        });
    };

    return { template, viewModel: ViewModel }
});
