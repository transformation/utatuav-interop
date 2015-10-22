/**
 * @fileoverview Service to interact with backend.
 * The data will be synced with the backend at a regular interval. You can
 * access the data via public fields of the service. When data is updated it
 * will broadcast an 'Backend.dataUpdated' event.
 */


/**
 * Service to interact with the backend.
 * @param {!angular.Scope} $rootScope The root scope service.
 * @param {!angular.Resource} $resource The resource service.
 * @param {!angular.$interval} $interval The interval service.
 * @final
 * @constructor
 * @struct
 * @ngInject
 */
Backend = function($rootScope, $resource, $interval) {
    /**
     * @export {?Object} The missions data.
     */
    this.missions = null;

    /**
     * @export {?Object} The teams data.
     */
    this.teams = null;

    /**
     * @export {?Object} The obstacles data.
     */
    this.obstacles = null;

    /**
     * @export {?Object} The telemetry data.
     */
    this.telemetry = null;

    /**
     * @private @const {!angular.Scope} The root scope service.
     */
    this.rootScope_ = $rootScope;

    /**
     * @private @const {!Object} Missions backend interface.
     */
    this.missionResource_ = $resource('/api/missions');

    /**
     * @private @const {!Object} Teams backend interface.
     */
    this.teamsResource_ = $resource('/api/teams');

    /**
     * @private @const {!Object} Obstacles backend interface.
     */
    this.obstaclesResource_ = $resource('/api/obstacles', {log: false});

    /**
     * @private @const {!Object} Telemetry backend interface.
     */
    this.telemetryResource_ = $resource('/api/telemetry');

    /**
     * @private @const {!Number} The update period in ms.
     */
    this.updatePeriodMs_ = 1000;
    /**
     * @private @const {!Object} The update which syncs with the backend (1s).
     */
    this.updateInterval_ = $interval(angular.bind(this, this.update_),
                                     this.updatePeriodMs_);
};


/**
 * Executes asynchronous updates with the backend.
 * @private
 */
Backend.prototype.update_ = function() {
    // Execute all asynchronous background syncs.
    this.missionResource_.query({}).$promise.then(
            angular.bind(this, this.setMissions_));
    this.teamsResource_.query({}).$promise.then(
            angular.bind(this, this.setTeams_));
    this.obstaclesResource_.get({}).$promise.then(
            angular.bind(this, this.setObstacles_));
    this.telemetryResource_.query({limit: 1}).$promise.then(
            angular.bind(this, this.setTelemetry_));
};


/**
 * Notifies others of data change by broadcasting an event.
 * @private
 */
Backend.prototype.notifyDataUpdated_ = function() {
    this.rootScope_.$broadcast('Backend.dataUpdated');
};


/**
 * Sets the missions.
 * @param {!Object} missions The missions to set.
 * @private
 */
Backend.prototype.setMissions_ = function(missions) {
    this.missions = missions;
    this.notifyDataUpdated_();
};


/**
 * Sets the teams.
 * @param {!Object} teams The teams to set.
 * @private
 */
Backend.prototype.setTeams_ = function(teams) {
    this.teams = teams;
    this.notifyDataUpdated_();
};


/**
 * Sets the obstacles.
 * @param {!Object} obstacles The obstacles to set.
 * @private
 */
Backend.prototype.setObstacles_ = function(obstacles) {
    this.obstacles = obstacles;
    this.notifyDataUpdated_();
};


/**
 * Sets the telemetry.
 * @param {!Object} telemetry The telemetry to set.
 * @private
 */
Backend.prototype.setTelemetry_ = function(telemetry) {
    this.telemetry = telemetry;
    this.notifyDataUpdated_();
};


// Register the service.
angular.module('auvsiSuasApp').service('Backend', [
    '$rootScope',
    '$resource',
    '$interval',
    Backend
]);
