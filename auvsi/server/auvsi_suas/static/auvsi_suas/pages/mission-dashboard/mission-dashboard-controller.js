/**
 * Controller for the Mission Dashboard page.
 */



/**
 * Controller for the Mission Dashboard page.
 * @param {!angular.Scope} $rootScope The root scope to listen for events.
 * @param {!angular.$routeParams} $routeParams The route parameter service.
 * @param {!Object} Backend The backend service.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
MissionDashboardCtrl = function($rootScope, $routeParams, Backend) {
    /**
     * @private @const {!angular.$routeParams} The route params service.
     */
    this.routeParams_ = $routeParams;

    /**
     * @private @const {!Object} The backend service.
     */
    this.backend_ = Backend;

    /**
     * @private @const {?Object} The scene built by the map view, via template.
     */
    this.missionScene = null;

    // Whenever the backend data is updated, rebuild the scene.
    $rootScope.$on(
            'Backend.dataUpdated',
            angular.bind(this, this.rebuildMissionScene_));
};


/**
 * Gets the current mission.
 * @return {?Object} The current mission.
 * @export
 */
MissionDashboardCtrl.prototype.getCurrentMission = function() {
    var missionId = this.routeParams_['missionId'];
    if (!missionId || !this.backend_.missions) {
        return null;
    }

    for (var i = 0; i < this.backend_.missions.length; i++) {
        var mission = this.backend_.missions[i];
        if (mission.id == missionId) {
            return mission;
        }
    }

    return null;
};


/**
 * Rebuild the mission scene using the backend data.
 * @private
 */
MissionDashboardCtrl.prototype.rebuildMissionScene_ = function() {
    if (!!this.missionScene) {
        // Rebuild scene with current mission.
        this.missionScene.rebuildScene(
                this.getCurrentMission(), this.backend_.obstacles,
                this.backend_.telemetry);
    }
};


/**
 * Determines whether a team is active or in-air.
 * @param {!Object} team The team to test.
 * @return {!boolean} Whether team is active or in-air.
 * @private
 */
MissionDashboardCtrl.prototype.isTeamActiveOrInAir_ = function(team) {
    return team.active || team.in_air;
};


/**
 * Gets the class used to color a team's display on the dashboard.
 * @param {!Object} team The team to get the color class for.
 * @return {!string} The color class.
 * @export
 */
MissionDashboardCtrl.prototype.getTeamColorClass = function(team) {
    if (team.active && team.in_air) {
        return 'mission-dashboard-team-active-and-in-air';
    } else if (team.active) {
        return 'mission-dashboard-team-active';
    } else if (team.in_air) {
        return 'mission-dashboard-team-in-air';
    } else {
        return 'mission-dashboard-team-inactive-and-not-in-air';
    }

};


/**
 * Gets a list of teams which are active or in-air.
 * @return {!Array} A list of teams which are active or in-air.
 * @export
 */
MissionDashboardCtrl.prototype.getActiveOrInAirTeams = function() {
    // Check that data has been loaded.
    if (!this.backend_.teams || this.backend_.teams.length == 0) {
        return [];
    }

    // Get all teams which are relevant.
    teams = [];
    for (var i = 0; i < this.backend_.teams.length; i++) {
        if (this.isTeamActiveOrInAir_(this.backend_.teams[i])) {
            teams.push(this.backend_.teams[i]);
        }
    }
    return teams;
};


// Register controller with app.
angular.module('auvsiSuasApp').controller('MissionDashboardCtrl', [
    '$rootScope',
    '$routeParams',
    'Backend',
    MissionDashboardCtrl
]);
