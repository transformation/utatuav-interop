/**
 * Tests for the Backend service.
 */


describe("Backend service", function() {
    var rootScope, interval, httpBackend;
    var backend;
    var missions, teams, telemetry, obstacles;

    beforeEach(module('auvsiSuasApp'));

    beforeEach(inject(function($rootScope, $interval, $httpBackend, Backend) {
        rootScope = $rootScope;
        interval = $interval;
        httpBackend = $httpBackend;
        backend = Backend;

        // Mock data, contents unimportant.
        missions = [{id: 1}];
        teams = [{id: 100}];
        telemetry = [{id: 200}];
        obstacles = {id: 300};

        $httpBackend.whenGET('/api/missions').respond(missions);
        $httpBackend.whenGET('/api/teams').respond(teams);
        $httpBackend.whenGET('/api/telemetry?limit=1').respond(telemetry);
        $httpBackend.whenGET('/api/obstacles?log=false')
            .respond(obstacles);
    }));

    it("Should initially have null fields", function() {
        expect(backend.missions).toBe(null);
        expect(backend.teams).toBe(null);
        expect(backend.telemetry).toBe(null);
        expect(backend.obstacles).toBe(null);
    });

    it("Should sync with backend", function() {
        interval.flush(backend.updatePeriodMs_);
        httpBackend.flush();
        expect(backend.missions[0].id).toEqual(missions[0].id);
        expect(backend.teams[0].id).toEqual(teams[0].id);
        expect(backend.telemetry[0].id).toEqual(telemetry[0].id);
        expect(backend.obstacles.id).toEqual(obstacles.id);
    });

    it("Should notify data updated", function() {
        var notified = false;
        rootScope.$on('Backend.dataUpdated', function() {
            notified = true;
        });

        interval.flush(backend.updatePeriodMs_);
        httpBackend.flush();
        expect(notified).toBe(true);
    });
});
