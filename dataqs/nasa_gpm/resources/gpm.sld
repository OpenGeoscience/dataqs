<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>nasa_gpm</sld:Name>
    <sld:UserStyle>
      <sld:Name>nasa_gpm</sld:Name>
      <sld:Title>NASA GPM Precipitation Estimate</sld:Title>
      <sld:IsDefault>1</sld:IsDefault>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ColorMap>
              <sld:ColorMapEntry color="#000000" opacity="0" quantity="-1" label="No Data"/>
              <sld:ColorMapEntry color="#110AF5" opacity="1" quantity="10" label="1 mm"/>
              <sld:ColorMapEntry color="#166CDE" opacity="1" quantity="50" label="5 mm"/>
              <sld:ColorMapEntry color="#12EFD9" opacity="1" quantity="100" label="10 mm"/>
              <sld:ColorMapEntry color="#30B60E" opacity="1" quantity="250" label="25/mm"/>
              <sld:ColorMapEntry color="#F6EE09" opacity="1" quantity="500" label="50 mm"/>
              <sld:ColorMapEntry color="#F3830A" opacity="1" quantity="750" label="75 mm"/>
              <sld:ColorMapEntry color="#F41708" opacity="1" quantity="1000" label="100 mm"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>