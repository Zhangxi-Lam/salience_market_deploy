import { html, PolymerElement } from '/static/otree-redwood/node_modules/@polymer/polymer/polymer-element.js';
import '/static/otree-redwood/src/otree-constants/otree-constants.js';
import '/static/otree-redwood/node_modules/@polymer/polymer/lib/elements/dom-repeat.js';

/*
    this component represents a list of trades which have occured in this market.
    it expects `trades` to be a sorted list of objects representing trades
*/

export class TradeList extends PolymerElement {

    static get properties() {
        return {
            trades: Array,
            assetName: String,
            displayFormat: {
                type: Object,
                value: function () {
                    return (making_order, taking_order) => `${making_order.traded_volume} @ $${making_order.price}`;
                },
            },
        };
    }

    static get template() {
        return html`
            <style>
                #container {
                    width: 100%;
                    height: 100%;
                    overflow-y: auto;
                    box-sizing: border-box;
                }
                #container div {
                    border: 1px solid black;
                    text-align: center;
                    margin: 3px;
                }
                .my-bid {
                    background-color: Bisque
                }
                .my-ask {
                    background-color: DeepSkyBlue
                }
            </style>

            <otree-constants
                id="constants"
            ></otree-constants>

            <div id="container">
                <template is="dom-repeat" items="{{trades}}" as="trade" filter="{{_getAssetFilterFunc(assetName)}}">
                    <template is="dom-repeat" items="{{trade.making_orders}}" as="making_order">
                        <div class$="[[_getTradeClass(trade)]]">
                            <span>[[displayFormat(making_order, trade.taking_order)]]</span>
                        </div>
                    </template>
                </template>
            </div>
        `;
    }

    ready() {
        super.ready();
        this.pcode = this.$.constants.participantCode;
    }

    _getAssetFilterFunc(assetName) {
        if (!assetName) {
            return null;
        }
        return function (trade) {
            return trade.asset_name == assetName;
        }
    }

    _getTradeClass(trade) {
        console.log(trade);
        if (trade.making_orders[0].pcode == this.pcode) {
            return trade.making_orders[0].is_bid ? 'my-bid' : 'my-ask';
        }
        if (trade.taking_order.pcode == this.pcode) {
            return trade.taking_order.is_bid ? 'my-bid' : 'my-ask';
        }
    }

}

window.customElements.define('trade-list', TradeList);
