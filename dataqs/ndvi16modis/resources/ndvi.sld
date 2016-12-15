<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>ndvi16modis</sld:Name>
    <sld:UserStyle>
      <sld:Name>ndvi16modis</sld:Name>
      <sld:Title>TerraMODIS 16-Day NDVI</sld:Title>
      <sld:IsDefault>1</sld:IsDefault>
      <sld:FeatureTypeStyle>
        <sld:Name>ndvi16modis</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ColorMap>
                            <sld:ColorMapEntry color="#ffffcc" label="0.000000" opacity="1.0" quantity="0"/>
                            <sld:ColorMapEntry color="#d6eeaa" label="0.15" opacity="1.0" quantity="0.15"/>
                            <sld:ColorMapEntry color="#a9db8e" label="0.30" opacity="1.0" quantity="0.3"/>
                            <sld:ColorMapEntry color="#78c679" label="0.45" opacity="1.0" quantity="0.45"/>
                            <sld:ColorMapEntry color="#48ae60" label="0.6" opacity="1.0" quantity="0.6"/>
                            <sld:ColorMapEntry color="#208f4a" label="0.85" opacity="1.0" quantity="0.85"/>
                            <sld:ColorMapEntry color="#006837" label="1.0" opacity="1.0" quantity="1"/>
                            <sld:ColorMapEntry color="#ffffff" label="No Data" opacity="1.0" quantity="99999"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>