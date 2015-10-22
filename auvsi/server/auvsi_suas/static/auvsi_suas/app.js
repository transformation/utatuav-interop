/**
 * @fileoverview Main application definition. This sets up the angular module
 * and the routes.
 */


/**
 * @export {!angular.Module} Application module.
 */
var auvsiSuasApp = angular.module('auvsiSuasApp', [
    'ngResource',
    'ngRoute'
]);


// Configure routes to templates and controllers.
auvsiSuasApp.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
        when('/', {
            templateUrl: '/static/auvsi_suas/pages/mission-list/mission-list.html',
            controller: 'MissionListCtrl',
            controllerAs: 'missionListCtrl'
        }).
        when('/mission/:missionId', {
            templateUrl: '/static/auvsi_suas/pages/mission-dashboard/mission-dashboard.html',
            controller: 'MissionDashboardCtrl',
            controllerAs: 'missionDashboardCtrl'
        }).
        otherwise({
            redirectTo: '/'
        });
}]);
