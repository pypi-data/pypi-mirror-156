/* globals geo */
import _ from 'underscore';
import $ from 'jquery';

import events from '@girder/core/events';
import Panel from '@girder/slicer_cli_web/views/Panel';

import convertAnnotation from '@girder/large_image_annotation/annotations/geojs/convert';
import convertRectangle from '@girder/large_image_annotation/annotations/geometry/rectangle';
import convertEllipse from '@girder/large_image_annotation/annotations/geometry/ellipse';
import convertCircle from '@girder/large_image_annotation/annotations/geometry/circle';

import StyleCollection from '../collections/StyleCollection';
import StyleModel from '../models/StyleModel';
import editElement from '../dialogs/editElement';
import editStyleGroups from '../dialogs/editStyleGroups';
import drawWidget from '../templates/panels/drawWidget.pug';
import drawWidgetElement from '../templates/panels/drawWidgetElement.pug';
import '../stylesheets/panels/drawWidget.styl';

/**
 * Create a panel with controls to draw and edit
 * annotation elements.
 */
var DrawWidget = Panel.extend({
    events: _.extend(Panel.prototype.events, {
        'click .h-edit-element': 'editElement',
        'click .h-view-element': 'viewElement',
        'click .h-delete-element': 'deleteElement',
        'click .h-draw': 'drawElement',
        'change .h-style-group': '_setToSelectedStyleGroup',
        'click .h-configure-style-group': '_styleGroupEditor',
        'mouseenter .h-element': '_highlightElement',
        'mouseleave .h-element': '_unhighlightElement'
    }),

    /**
     * Create the panel.
     *
     * @param {object} settings
     * @param {ItemModel} settings.image
     *     The associate large_image "item"
     */
    initialize(settings) {
        this.image = settings.image;
        this.annotation = settings.annotation;
        this.collection = this.annotation.elements();
        this.viewer = settings.viewer;
        this.setViewer(settings.viewer);
        this.setAnnotationSelector(settings.annotationSelector);
        this._drawingType = settings.drawingType || null;

        this._highlighted = {};
        this._groups = new StyleCollection();
        this._style = new StyleModel({id: 'default'});
        this.listenTo(this._groups, 'add change', this._handleStyleGroupsUpdate);
        this.listenTo(this._groups, 'remove', this.render);
        this.listenTo(this.collection, 'add remove reset', this._recalculateGroupAggregation);
        this.listenTo(this.collection, 'change update reset', this.render);
        this._groups.fetch().done(() => {
            // ensure the default style exists
            if (this._groups.has('default')) {
                this._style.set(this._groups.get('default').toJSON());
            } else {
                this._groups.add(this._style.toJSON());
                this._groups.get(this._style.id).save();
            }
        });
        this.on('h:mouseon', (model) => {
            if (model && model.id) {
                this._highlighted[model.id] = true;
                this.$(`.h-element[data-id="${model.id}"]`).addClass('h-highlight-element');
            }
        });
        this.on('h:mouseoff', (model) => {
            if (model && model.id) {
                this._highlighted[model.id] = false;
                this.$(`.h-element[data-id="${model.id}"]`).removeClass('h-highlight-element');
            }
        });
    },

    render(updatedElement) {
        if (!this.viewer) {
            this.$el.empty();
            delete this._skipRenderHTML;
            return;
        }
        const name = (this.annotation.get('annotation') || {}).name || 'Untitled';
        if (!updatedElement || (updatedElement.attributes && updatedElement.get('type') !== 'pixelmap')) {
            this.trigger('h:redraw', this.annotation);
        }
        if (this._skipRenderHTML) {
            delete this._skipRenderHTML;
        } else {
            this.$el.html(drawWidget({
                title: 'Draw',
                elements: this.collection.models,
                groups: this._groups,
                style: this._style.id,
                highlighted: this._highlighted,
                name,
                collapsed: this.$('.s-panel-content.collapse').length && !this.$('.s-panel-content').hasClass('in')
            }));
        }
        this.$('button.h-draw[data-type]').removeClass('active');
        if (this._drawingType) {
            this.$('button.h-draw[data-type="' + this._drawingType + '"]').addClass('active');
            this.drawElement(undefined, this._drawingType);
        }
        if (this.viewer.annotationLayer && this.viewer.annotationLayer._boundHUIModeChange === undefined) {
            this.viewer.annotationLayer._boundHUIModeChange = true;
            this.viewer.annotationLayer.geoOn(geo.event.annotation.mode, (event) => {
                if (event.mode === this.viewer.annotationLayer.modes.edit || event.oldmode === this.viewer.annotationLayer.modes.edit) {
                    return;
                }
                this.$('button.h-draw').removeClass('active');
                if (this._drawingType) {
                    this.$('button.h-draw[data-type="' + this._drawingType + '"]').addClass('active');
                }
                if (event.mode !== this._drawingType && this._drawingType) {
                    /* This makes the draw modes stay on until toggled off.
                     * To turn off drawing after each annotation, add
                     *  this._drawingType = null;
                     */
                    this.drawElement(undefined, this._drawingType);
                }
            });
        }
        return this;
    },

    /**
     * When a region should be drawn that isn't caused by a drawing button,
     * toggle off the drawing mode.
     *
     * @param {event} Girder event that triggered drawing a region.
     */
    _widgetDrawRegion(evt) {
        this._drawingType = null;
        this.$('button.h-draw').removeClass('active');
    },

    /**
     * Set the image "viewer" instance.  This should be a subclass
     * of `large_image/imageViewerWidget` that is capable of rendering
     * annotations.
     */
    setViewer(viewer) {
        this.viewer = viewer;
        // make sure our listeners are in the correct order.
        this.stopListening(events, 's:widgetDrawRegion', this._widgetDrawRegion);
        if (viewer) {
            this.listenTo(events, 's:widgetDrawRegion', this._widgetDrawRegion);
            viewer.stopListening(events, 's:widgetDrawRegion', viewer.drawRegion);
            viewer.listenTo(events, 's:widgetDrawRegion', viewer.drawRegion);
        }
        return this;
    },

    /**
     * Set the image 'annotationSelector' instance.
     */
    setAnnotationSelector(annotationSelector) {
        this.annotationSelector = annotationSelector;
        return this;
    },

    /**
     * Respond to a click on the "edit" button by rendering
     * the EditAnnotation modal dialog.
     */
    editElement(evt) {
        var dialog = editElement(this.collection.get(this._getId(evt)));
        this.listenTo(dialog, 'h:editElement', (obj) => {
            // update the html immediately instead of rerendering it
            let id = obj.element.id,
                label = (obj.data.label || {}).value,
                elemType = obj.element.get('type');
            label = label || (elemType === 'polyline' ? (obj.element.get('closed') ? 'polygon' : 'line') : elemType);
            this.$(`.h-element[data-id="${id}"] .h-element-label`).text(label).attr('title', label);
            this._skipRenderHTML = true;
        });
    },

    /**
     * Respond to a click on the "view" button by changing the
     * viewer location and zoom level to focus on one annotation
     */
    viewElement(evt) {
        const annot = this.collection._byId[$(evt.target).parent().attr('data-id')];
        let points;
        let pointAnnot = false;
        switch (annot.get('type')) {
            case 'point':
                points = [annot.get('center')];
                pointAnnot = true;
                break;
            case 'polyline':
                points = annot.get('points');
                break;
            case 'rectangle':
                points = convertRectangle(annot.attributes).coordinates[0];
                break;
            case 'ellipse':
                points = convertEllipse(annot.attributes).coordinates[0];
                break;
            case 'circle':
                points = convertCircle(annot.attributes).coordinates[0];
                break;
        }
        const xCoords = points.map((point) => point[0]);
        const yCoords = points.map((point) => point[1]);
        const bounds = {
            left: Math.min(...xCoords),
            top: Math.min(...yCoords),
            right: Math.max(...xCoords),
            bottom: Math.max(...yCoords)
        };
        const map = this.parentView.viewer;
        const originalZoomRange = map.zoomRange();
        map.zoomRange({
            min: Number.NEGATIVE_INFINITY,
            max: Number.POSITIVE_INFINITY
        });
        const newView = pointAnnot
            ? {
                center: {
                    x: bounds.left,
                    y: bounds.top
                },
                zoom: false
            }
            : map.zoomAndCenterFromBounds(bounds, map.rotation());
        map.zoomRange({
            min: originalZoomRange.origMin,
            max: originalZoomRange.max
        });
        if (Math.abs(newView.zoom - 1.5 - map.zoom()) <= 0.5 && map.zoom() < newView.zoom) {
            newView.zoom = false;
        }
        const distance = ((newView.center.x - map.center().x) ** 2 + (newView.center.y - map.center().y) ** 2) ** 0.5;
        map.transition({
            center: newView.center,
            zoom: newView.zoom === false ? map.zoom() : newView.zoom - 1.5,
            duration: Math.min(1000, Math.max(100, distance)),
            endClamp: false,
            interp: distance < 500 ? undefined : window.d3.interpolateZoom,
            ease: window.d3.easeExpInOut
        });
        this._skipRenderHTML = true;
    },

    /**
     * Respond to a click on the "delete" button by removing
     * the element from the element collection.
     */
    deleteElement(evt, id, opts) {
        if (evt) {
            id = this._getId(evt);
        }
        this.$(`.h-element[data-id="${id}"]`).remove();
        this._skipRenderHTML = true;
        this.collection.remove(id, opts);
    },

    /**
     * Add a list of elements, updating the element container efficiently.
     *
     * @params {object[]} elements The list of elements to add to the
     *    collection.
     */
    addElements(elements) {
        this._skipRenderHTML = true;
        elements = this.collection.add(elements);
        this.$el.find('.h-elements-container').append(
            drawWidgetElement({
                elements: elements,
                style: this._style.id,
                highlighted: this._highlighted
            })
        );
    },

    /**
     * Apply a boolean operation to the existign polygons.
     *
     * @param {object[]} element A list of elements that were specified.
     * @param {geo.annotation[]} annotations The list of specified geojs
     *      annotations.
     * @param {object} opts An object with the current boolean operation.
     * @returns {boolean} true if the operation was handled.
     */
    _applyBooleanOp(element, annotations, evtOpts) {
        if (annotations.length !== 1 || !annotations[0].toPolygonList) {
            return false;
        }
        const op = evtOpts.currentBooleanOperation;
        const existing = this.viewer._annotations[this.annotation.id].features.filter((f) => ['polygon', 'marker'].indexOf(f.featureType) >= 0);
        if (!existing.length) {
            return false;
        }
        const near = existing.map((f) => f.polygonSearch(
            annotations[0].toPolygonList()[0][0].map((pt) => ({x: pt[0], y: pt[1]})),
            {partial: true}, null));
        if (!near.some((n) => n.found.length)) {
            return false;
        }
        const oldids = {};
        const geojson = {type: 'FeatureCollection', features: []};
        near.forEach((n) => n.found.forEach((element) => {
            // filter to match current style group
            if (element.properties.element && element.properties.element.group !== this._style.get('group')) {
                return;
            }
            element.properties.annotationId = element.properties.annotation;
            geojson.features.push(element);
            oldids[element.id] = true;
        }));
        if (!geojson.features.length) {
            return false;
        }
        this.viewer.annotationLayer.removeAllAnnotations(undefined, false);
        this.viewer.annotationLayer.geojson(geojson);
        const opts = {
            correspond: {},
            keepAnnotations: 'exact',
            style: this.viewer.annotationLayer
        };
        geo.util.polyops[op](this.viewer.annotationLayer, annotations[0], opts);
        const newAnnot = this.viewer.annotationLayer.annotations();

        this.viewer.annotationLayer.removeAllAnnotations(undefined, false);
        Object.keys(oldids).forEach((id) => this.deleteElement(undefined, id, {silent: true}));
        element = newAnnot.map((annot) => {
            const result = convertAnnotation(annot);
            if (!result.id) {
                result.id = this.viewer._guid();
            }
            return result;
        });
        this.addElements(
            _.map(element, (el) => {
                el = _.extend(el, _.omit(this._style.toJSON(), 'id'));
                if (!this._style.get('group')) {
                    delete el.group;
                }
                return el;
            })
        );
        return true;
    },

    /**
     * Respond to clicking an element type by putting the image viewer into
     * "draw" mode.
     *
     * @param {jQuery.Event} [evt] The button click that triggered this event.
     *      `undefined` to use a passed-in type.
     * @param {string|null} [type] If `evt` is `undefined`, switch to this draw
     *      mode.
     */
    drawElement(evt, type) {
        var $el;
        if (evt) {
            $el = this.$(evt.currentTarget);
            $el.tooltip('hide');
            type = $el.hasClass('active') ? null : $el.data('type');
        } else {
            $el = this.$('button.h-draw[data-type="' + type + '"]');
        }
        if (this.viewer.annotationLayer.mode() === type && this._drawingType === type && (!type || this.viewer.annotationLayer.currentAnnotation)) {
            return;
        }
        if (this.viewer.annotationLayer.mode()) {
            this._drawingType = null;
            this.viewer.annotationLayer.mode(null);
            this.viewer.annotationLayer.geoOff(geo.event.annotation.state);
            this.viewer.annotationLayer.removeAllAnnotations();
        }
        if (type) {
            this.parentView._resetSelection();
            // always show the active annotation when drawing a new element
            this.annotation.set('displayed', true);

            this._drawingType = type;
            this.viewer.startDrawMode(type)
                .then((element, annotations, opts) => {
                    opts = opts || {};
                    if (opts.currentBooleanOperation) {
                        const processed = this._applyBooleanOp(element, annotations, opts);
                        if (processed || ['difference', 'intersect'].indexOf(opts.currentBooleanOperation) >= 0) {
                            this.drawElement(undefined, this._drawingType);
                            return undefined;
                        }
                    }
                    // add current style group information
                    this.addElements(
                        _.map(element, (el) => {
                            el = _.extend(el, _.omit(this._style.toJSON(), 'id'));
                            if (!this._style.get('group')) {
                                delete el.group;
                            }
                            return el;
                        })
                    );
                    this.drawElement(undefined, this._drawingType);
                    return undefined;
                });
        }
        this.$('button.h-draw[data-type]').removeClass('active');
        if (this._drawingType) {
            this.$('button.h-draw[data-type="' + this._drawingType + '"]').addClass('active');
        }
    },

    cancelDrawMode() {
        this.drawElement(undefined, null);
        this.viewer.annotationLayer._boundHUIModeChange = false;
        this.viewer.annotationLayer.geoOff(geo.event.annotation.state);
    },

    drawingType() {
        return this._drawingType;
    },

    /**
     * Get the element id from a click event.
     */
    _getId(evt) {
        return this.$(evt.currentTarget).parent('.h-element').data('id');
    },

    _setStyleGroup(group) {
        this._style.set(group);
        if (!this._style.get('group') && this._style.id !== 'default') {
            this._style.set('group', this._style.id);
        } else if (this._style.get('group') && this._style.id === 'default') {
            this._style.unset('group');
        }
        this.$('.h-style-group').val(group.id);
    },

    _setToSelectedStyleGroup() {
        this._setStyleGroup(this._groups.get(this.$('.h-style-group').val()).toJSON());
    },

    /**
     * Set the style group to the next available group in the dropdown.
     *
     * If the currently selected group is the last group in the dropdown,
     * the first group in the dropdown is selected instead.
     */
    setToNextStyleGroup() {
        let nextGroup = this.$('.h-style-group option:selected').next().val();
        // A style group can have an empty string for a name, so we must explicitly
        // test if this is undefined instead of just testing truthiness.
        if (nextGroup === undefined) {
            nextGroup = this.$('.h-style-group option:first').val();
        }
        this._setStyleGroup(this._groups.get(nextGroup).toJSON());
    },

    /**
     * Set the style group to the previous available group in the dropdown.
     *
     * If the currently selected group is the first group in the dropdown,
     * the last group in the dropdown is selected instead.
     */
    setToPrevStyleGroup() {
        let prevGroup = this.$('.h-style-group option:selected').prev().val();
        // A style group can have an empty string for a name, so we must explicitly
        // test if this is undefined instead of just testing truthiness.
        if (prevGroup === undefined) {
            prevGroup = this.$('.h-style-group option:last-child').val();
        }
        this._setStyleGroup(this._groups.get(prevGroup).toJSON());
    },

    getStyleGroup() {
        return this._style;
    },

    _styleGroupEditor() {
        var dlg = editStyleGroups(this._style, this._groups);
        dlg.$el.on('hidden.bs.modal', () => {
            this.render();
            this.parentView.trigger('h:styleGroupsEdited', this._groups);
        });
    },

    _handleStyleGroupsUpdate() {
        this.render();
        this.trigger('h:styleGroupsUpdated', this._groups);
    },

    _highlightElement(evt) {
        const id = $(evt.currentTarget).data('id');
        const annotType = this.collection._byId[id].get('type');
        if (this.annotationSelector._interactiveMode && ['point', 'polyline', 'rectangle', 'ellipse', 'circle'].includes(annotType)) {
            $(evt.currentTarget).find('.h-view-element').show();
        }
        this.parentView.trigger('h:highlightAnnotation', this.annotation.id, id);
    },

    _unhighlightElement(evt) {
        $(evt.currentTarget).find('.h-view-element').hide();
        this.parentView.trigger('h:highlightAnnotation');
    },

    _recalculateGroupAggregation() {
        const groups = [];
        const used = {};
        this.collection.forEach((el) => {
            const group = el.get('group') || '__null__';
            if (!used[group]) {
                used[group] = true;
                if (group !== '__null__') {
                    groups.push(group);
                }
            }
        });
        if (used.__null__) {
            groups.push(null);
        }
        this.annotation.set('groups', groups);
    }
});

export default DrawWidget;
