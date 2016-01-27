<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>airnow</sld:Name>
    <sld:UserStyle>
      <sld:Name>airnow</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Geometry>
              <ogc:PropertyName>grid</ogc:PropertyName>
            </sld:Geometry>
            <sld:ColorMap>
              <sld:ColorMapEntry color="#008000" opacity="1.0" quantity="0" label="Good"/>
              <sld:ColorMapEntry color="#FFFF00" opacity="1.0" quantity="50" label="Moderate"/>
              <sld:ColorMapEntry color="#FFA500" opacity="1.0" quantity="100" label="Unhealthy for Sensitive Groups"/>
              <sld:ColorMapEntry color="#FF0000" opacity="1.0" quantity="150" label="Unhealthy"/>
              <sld:ColorMapEntry color="#800080" opacity="1.0" quantity="200" label="Very Unhealthy"/>
              <sld:ColorMapEntry color="#800000" opacity="1.0" quantity="300" label="Hazardous"/>
              <sld:ColorMapEntry color="#008000" opacity="0.0001" quantity="500" label=""/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>