/**
 * Tests for the MissionListCtrl controller.
 */


describe("MissionListCtrl controller", function() {
    var backend, missionListCtrl;

    beforeEach(module('auvsiSuasApp'));

    beforeEach(inject(function($controller) {
        backend = {missions: null};
        missionListCtrl = $controller('MissionListCtrl', {Backend: backend});
    }));

    it("Shouldn't have missions with null list", function() {
        expect(missionListCtrl.hasMissions()).toBe(false);
    });

    it("Shouldn't have missions with empty list", function() {
        backend.missions = [];
        expect(missionListCtrl.hasMissions()).toBe(false);
    });

    it("Should have missions with non-empty list", function() {
        backend.missions = [{id: 1}];
        expect(missionListCtrl.hasMissions()).toBe(true);
    });
});
