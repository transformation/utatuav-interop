/**
 * Tests for the MissionDashboardCtrl controller.
 */


describe("MissionDashboardCtrl controller", function() {
    var routeParams, backend;
    var missionDashboardCtrl;

    beforeEach(module('auvsiSuasApp'));

    beforeEach(inject(function($rootScope, $controller) {
        routeParams = {
            missionId: 1
        };
        backend = {
            missions: [{id: 1}, {id: 2}],
            obstacles: [],
        };

        missionDashboardCtrl = $controller('MissionDashboardCtrl',
                                           {$rootScope: $rootScope,
                                            $routeParams: routeParams,
                                            Backend: backend});
    }));

    it("Should get current mission", function() {
        expect(missionDashboardCtrl.getCurrentMission()).toEqual({id: 1});

        routeParams.missionId = 1000;
        expect(missionDashboardCtrl.getCurrentMission()).toBe(null);

        missions = backend.missions;
        backend.missions = null;
        expect(missionDashboardCtrl.getCurrentMission()).toBe(null);
        backend.missions = missions;

        routeParams.missionId = null;
        expect(missionDashboardCtrl.getCurrentMission()).toBe(null);
    });

    it("Should get the team color class", function() {
        var team = {
            active: true,
            in_air: true
        };
        expect(missionDashboardCtrl.getTeamColorClass(team))
            .toEqual('mission-dashboard-team-active-and-in-air');

        team.in_air = false;
        team.active = true;
        expect(missionDashboardCtrl.getTeamColorClass(team))
            .toEqual('mission-dashboard-team-active');

        team.in_air = true;
        team.active = false;
        expect(missionDashboardCtrl.getTeamColorClass(team))
            .toEqual('mission-dashboard-team-in-air');

        team.in_air = false;
        team.active = false;
        expect(missionDashboardCtrl.getTeamColorClass(team))
            .toEqual('mission-dashboard-team-inactive-and-not-in-air');
    });

    it("Should get active or in air teams", function() {
        var teams = [
            {id: 1, active: false, in_air: false},
            {id: 2, active: true,  in_air: false},
            {id: 3, active: false, in_air: true},
            {id: 4, active: true,  in_air: true}
        ];
        active_or_in_air = [teams[1], teams[2], teams[3]];
        backend.teams = teams;

        expect(missionDashboardCtrl.getActiveOrInAirTeams())
            .toEqual(active_or_in_air);
    });
});
