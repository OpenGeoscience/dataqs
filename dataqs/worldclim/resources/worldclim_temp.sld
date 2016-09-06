<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>worldclim_temp</sld:Name>
    <sld:UserStyle>
      <sld:Name>worldclim_temp</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Geometry>
              <ogc:PropertyName>grid</ogc:PropertyName>
            </sld:Geometry>
            <sld:ColorMap>
              <sld:ColorMapEntry color="#2c7bb6" opacity="1.0" quantity="-500" label="-50 °C"/>
              <sld:ColorMapEntry color="#61a2cb" opacity="1.0" quantity="-250" label="-25 °C"/>
              <sld:ColorMapEntry color="#96cae0" opacity="1.0" quantity="-100" label="-10 °C"/>
              <sld:ColorMapEntry color="#c1e3dd" opacity="1.0" quantity="0" label="0 °C"/>
              <sld:ColorMapEntry color="#e4f3cc" opacity="1.0" quantity="50" label="5 °C"/>
              <sld:ColorMapEntry color="#fef6b5" opacity="1.0" quantity="100" label="10 °C"/>
              <sld:ColorMapEntry color="#fdd48d" opacity="1.0" quantity="150" label="15 °C"/>
              <sld:ColorMapEntry color="#fdb265" opacity="1.0" quantity="200" label="20 °C"/>
              <sld:ColorMapEntry color="#ef7747" opacity="1.0" quantity="250" label="25 °C"/>
              <sld:ColorMapEntry color="#d7191c" opacity="1.0" quantity="300" label="30 °C"/>
            </sld:ColorMap>
            <sld:ContrastEnhancement/>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
